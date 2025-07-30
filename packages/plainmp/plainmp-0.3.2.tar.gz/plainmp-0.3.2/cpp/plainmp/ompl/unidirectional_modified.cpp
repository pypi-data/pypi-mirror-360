/*
 * plainmp - library for fast motion planning
 *
 * Copyright (C) 2024 Hirokazu Ishida
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

/*********************************************************************
 * Software License Agreement (BSD License)
 *
 *  Copyright (c) 2008, Willow Garage, Inc.
 *  All rights reserved.
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *   * Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *   * Redistributions in binary form must reproduce the above
 *     copyright notice, this list of conditions and the following
 *     disclaimer in the documentation and/or other materials provided
 *     with the distribution.
 *   * Neither the name of the Willow Garage nor the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 *  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 *  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 *  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 *  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 *  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 *  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 *  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *  POSSIBILITY OF SUCH DAMAGE.
 *********************************************************************/

/* Author: Ioan Sucan */
/* Modified by plainmp */

#include "plainmp/ompl/unidirectional_modified.hpp"
#include <ompl/base/goals/GoalSampleableRegion.h>
#include <ompl/tools/config/SelfConfig.h>
#include <limits>

namespace ompl {
namespace custom {

base::PlannerStatus RRTModified::solve_with_goal_const(
    const base::PlannerTerminationCondition& ptc) {
  checkValidity();
  base::Goal* goal = pdef_->getGoal().get();
  auto* goal_s = dynamic_cast<base::GoalSampleableRegion*>(goal);

  while (const base::State* st = pis_.nextStart()) {
    auto* motion = new Motion(si_);
    si_->copyState(motion->state, st);
    nn_->add(motion);
  }

  if (nn_->size() == 0) {
    OMPL_ERROR("%s: There are no valid initial states!", getName().c_str());
    return base::PlannerStatus::INVALID_START;
  }

  if (!sampler_)
    sampler_ = si_->allocStateSampler();

  OMPL_INFORM("%s: Starting planning with %u states already in datastructure",
              getName().c_str(), nn_->size());

  Motion* solution = nullptr;
  Motion* approxsol = nullptr;
  double approxdif = std::numeric_limits<double>::infinity();
  auto* rmotion = new Motion(si_);
  base::State* rstate = rmotion->state;
  base::State* xstate = si_->allocState();

  while (!ptc) {
    /* sample random state (with goal biasing) */
    bool sample_goal = false;
    if ((goal_s != nullptr) && rng_.uniform01() < goalBias_ &&
        goal_s->canSample()) {
      goal_s->sampleGoal(rstate);
      sample_goal = true;
    } else {
      sampler_->sampleUniform(rstate);
    }

    /* find closest state in the tree */
    Motion* nmotion = nn_->nearest(rmotion);
    base::State* dstate = rstate;

    /* find state to add */
    bool reach_random = true;
    double d = si_->distance(nmotion->state, rstate);
    if (d > maxDistance_) {
      si_->getStateSpace()->interpolate(nmotion->state, rstate,
                                        maxDistance_ / d, xstate);
      dstate = xstate;
      reach_random = false;
    }

    if (si_->checkMotion(nmotion->state, dstate)) {
      if (addIntermediateStates_) {
        std::vector<base::State*> states;
        const unsigned int count =
            si_->getStateSpace()->validSegmentCount(nmotion->state, dstate);

        if (si_->getMotionStates(nmotion->state, dstate, states, count, true,
                                 true))
          si_->freeState(states[0]);

        for (std::size_t i = 1; i < states.size(); ++i) {
          auto* motion = new Motion;
          motion->state = states[i];
          motion->parent = nmotion;
          nn_->add(motion);

          nmotion = motion;
        }
      } else {
        auto* motion = new Motion(si_);
        si_->copyState(motion->state, dstate);
        motion->parent = nmotion;
        nn_->add(motion);

        nmotion = motion;
      }

      // we accept only when the motion to exact gaol is valid
      bool sat = sample_goal && reach_random;
      if (sat) {
        approxdif = 0.0;
        solution = nmotion;
        break;
      }
    }
  }

  bool solved = false;
  bool approximate = false;
  if (solution == nullptr) {
    solution = approxsol;
    approximate = true;
  }

  if (solution != nullptr) {
    lastGoalMotion_ = solution;

    /* construct the solution path */
    std::vector<Motion*> mpath;
    while (solution != nullptr) {
      mpath.push_back(solution);
      solution = solution->parent;
    }

    /* set the solution path */
    auto path(std::make_shared<geometric::PathGeometric>(si_));
    for (int i = mpath.size() - 1; i >= 0; --i)
      path->append(mpath[i]->state);
    pdef_->addSolutionPath(path, approximate, approxdif, getName());
    solved = true;
  }

  si_->freeState(xstate);
  if (rmotion->state != nullptr)
    si_->freeState(rmotion->state);
  delete rmotion;

  OMPL_INFORM("%s: Created %u states", getName().c_str(), nn_->size());

  return {solved, approximate};
}

base::PlannerStatus KPIECE1Modified::solve_with_goal_const(
    const base::PlannerTerminationCondition& ptc) {
  checkValidity();
  base::Goal* goal = pdef_->getGoal().get();
  auto* goal_s = dynamic_cast<base::GoalSampleableRegion*>(goal);

  geometric::Discretization<Motion>::Coord xcoord(
      projectionEvaluator_->getDimension());

  while (const base::State* st = pis_.nextStart()) {
    auto* motion = new Motion(si_);
    si_->copyState(motion->state, st);
    projectionEvaluator_->computeCoordinates(motion->state, xcoord);
    disc_.addMotion(motion, xcoord, 1.0);
  }

  if (disc_.getMotionCount() == 0) {
    OMPL_ERROR("%s: There are no valid initial states!", getName().c_str());
    return base::PlannerStatus::INVALID_START;
  }

  if (!sampler_)
    sampler_ = si_->allocStateSampler();

  OMPL_INFORM("%s: Starting planning with %u states already in datastructure",
              getName().c_str(), disc_.getMotionCount());

  Motion* solution = nullptr;
  Motion* approxsol = nullptr;
  double approxdif = std::numeric_limits<double>::infinity();
  base::State* xstate = si_->allocState();

  while (!ptc) {
    disc_.countIteration();

    /* Decide on a state to expand from */
    Motion* existing = nullptr;
    geometric::Discretization<Motion>::Cell* ecell = nullptr;
    disc_.selectMotion(existing, ecell);
    assert(existing);

    /* sample random state (with goal biasing) */
    bool sample_goal = false;
    if ((goal_s != nullptr) && rng_.uniform01() < goalBias_ &&
        goal_s->canSample()) {
      goal_s->sampleGoal(xstate);
      sample_goal = true;
    } else {
      sampler_->sampleUniformNear(xstate, existing->state, maxDistance_);
    }

    std::pair<base::State*, double> fail(xstate, 0.0);
    bool keep = si_->checkMotion(existing->state, xstate, fail);
    if (!keep && fail.second > minValidPathFraction_)
      keep = true;

    if (keep) {
      /* create a motion */
      auto* motion = new Motion(si_);
      si_->copyState(motion->state, xstate);
      motion->parent = existing;

      bool solv = sample_goal;  // if keep && sample_goal, then solv = true
      projectionEvaluator_->computeCoordinates(motion->state, xcoord);
      double dist =
          std::numeric_limits<double>::infinity();  // dummy value whatever
      disc_.addMotion(motion, xcoord,
                      dist);  // this will also update the discretization heaps
                              // as needed, so no call to updateCell() is needed

      if (solv) {
        approxdif = dist;
        solution = motion;
        break;
      }
      if (dist < approxdif) {
        approxdif = dist;
        approxsol = motion;
      }
    } else
      ecell->data->score *= failedExpansionScoreFactor_;
    disc_.updateCell(ecell);
  }

  bool solved = false;
  bool approximate = false;
  if (solution == nullptr) {
    solution = approxsol;
    approximate = true;
  }

  if (solution != nullptr) {
    lastGoalMotion_ = solution;

    /* construct the solution path */
    std::vector<Motion*> mpath;
    while (solution != nullptr) {
      mpath.push_back(solution);
      solution = solution->parent;
    }

    /* set the solution path */
    auto path(std::make_shared<geometric::PathGeometric>(si_));
    for (int i = mpath.size() - 1; i >= 0; --i)
      path->append(mpath[i]->state);
    pdef_->addSolutionPath(path, approximate, approxdif, getName());
    solved = true;
  }

  si_->freeState(xstate);

  OMPL_INFORM("%s: Created %u states in %u cells (%u internal + %u external)",
              getName().c_str(), disc_.getMotionCount(), disc_.getCellCount(),
              disc_.getGrid().countInternal(), disc_.getGrid().countExternal());

  return {solved, approximate};
}

}  // namespace custom
};  // namespace ompl
