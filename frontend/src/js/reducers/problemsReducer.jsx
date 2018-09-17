import clone from 'clone';
import * as _ from 'lodash';

import { STATUSES } from '../constants';


const initialState = {};


const normalizeRelated = (related, key) => {
  return _.chain(related)
    .groupBy(item => item.problemId)
    .mapValues(items => ({[key]: _.map(items, item => item.id)}))
    .value();
}
const normalizeRuns = (runs) => normalizeRelated(runs, 'runs');
const normalizeSubmits = (submits) => normalizeRelated(submits, 'submits');


const mergeProblem = (problem, data) => {
  problem = problem || {};

  let runs = problem.runs || [];
  if (_.has(data, 'runs')) {
    runs = _.union(runs, data.runs);
  }

  let submits = problem.submits || [];
  if (_.has(data, 'submits')) {
    submits = _.union(submits, data.submits);
  }

  return {
    ...problem,
    ...data,
    runs,
    submits,
  }
}

const mergeState = (state, ...updates) => {
  return _.mergeWith({...state}, ...updates, mergeProblem);
}


export default function reducer(state=initialState, action) {
  const {problemId, runId} = action.meta || {};

  switch (action.type) {
    case 'WEBSOCKET_MESSAGE':
      const { ejudge_error } = action.data;
      if (typeof ejudge_error !== 'undefined') {
        const { code, message } = ejudge_error;
        alert(code + ' ' + message);
      }

      const { runs } = action.data;
      const runsForMerge = _.chain(runs)
        .groupBy(run => run.problem_id)
        .mapValues(
          problemRuns => (
            { runs: _.keyBy(problemRuns, run => run.run_id) }
          )
        )
        .value();
      return _.merge({}, state, runsForMerge);

    case 'GET_PROBLEM_PENDING':
      return {
        ...state,
        [problemId]: {
          ...state[problemId],
          fetching: true,
        }
      };
    case 'GET_PROBLEM_FULFILLED':
      return {
        ...state,
        [problemId]: {
          ...state[problemId],
          fetching: false,
          fetched: true,
          data: action.payload.data,
        },
      };
    case 'GET_PROBLEM_REJECTED':
      return {
        ...state,
        [problemId]: {
          ...state[problemId],
          fetching: false,
          fetched: false,
        }
      };

    case 'GET_PROBLEM_RUNS_PENDING':
      return {
        ...state,
        [problemId]: {
          ...state[problemId],
          fetchingRuns: true,
        },
      };
    case 'GET_PROBLEM_RUNS_FULFILLED':
      return mergeState(
        state,
        {
          [problemId]: {
            fetchingRuns: false,
            fetchedRuns: true,
          }
        },
        normalizeRuns(action.payload.data),
      )
    case 'GET_PROBLEM_RUNS_REJECTED':
      return {
        ...state,
        [problemId]: {
          ...state[problemId],
          fetchingRuns: false,
          fetchedRuns: false,
        },
      };


    case 'GET_PROBLEM_RUN_PROTOCOL_PENDING':
      return state;
    case 'GET_PROBLEM_RUN_PROTOCOL_FULFILLED':
      const protocolData = action.payload.data;
      protocolData.tests = _.mapValues(protocolData.tests, testProtocol => ({
        ..._.omit(testProtocol, ['status', 'string_status']),
        status: parseInt(_.findKey(STATUSES, status => status.short === testProtocol.status)),
      }));

      return {
        ...state,
        [problemId]: {
          ...state[problemId],
          runs: {
            ...state[problemId].runs,
            [runId]: {
              ...state[problemId].runs[runId],
              protocol: protocolData,
            }
          }
        }
      };
    case 'GET_PROBLEM_RUN_PROTOCOL_REJECTED':
      return state;

    case 'GET_PROBLEM_STANDINGS_FULFILLED':
      return {
        ...state,
        [problemId]: {
          ...state[problemId],
          standings: actions.payload.data,
        }
      };

    case 'GET_USER_SUBMITS_FULFILLED':
      const newState = {...state};
      const submits = _.chain(action.payload.data.submits)
        .groupBy(submit => submit.problemId)
        .mapValues(submits => _.map(submits, submit => submit.id))
        .value();
      _.forEach(submits, (submitIds, problemId) => {
        newState[problemId] = {
          ...state[problemId],
          submits: _.union(_.get(state, `[${problemId}].submits`, []), submitIds),
        }
      })
      return newState;

    case 'POST_PROBLEM_SUBMIT_FULFILLED':
      const { submit } = action.payload.data;
      return mergeState(state, normalizeSubmits([submit]));

    case 'WEBSOCKET_GET_RUNS':
      return mergeState(
        state,
        normalizeRuns(action.payload),
      );
  }
  return state;
}