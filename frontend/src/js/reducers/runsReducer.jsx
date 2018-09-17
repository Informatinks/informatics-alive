import * as _ from 'lodash';

import { STATUSES } from '../constants';


const initialState = {};


const normalizeRun = (run) => ({
  ..._.omit(run, 'user'),
  userId: run.user.id,
})


const normalizeProtocol = (protocol) => ({
  ...protocol,
  tests: _.mapValues(protocol.tests, test => ({
    ..._.omit(test, 'status', 'stringStatus'),
    status: parseInt(_.findKey(STATUSES, status => status.short === test.status)),
  })),
})


export default function reducer(state=initialState, action) {
  switch (action.type) {
    case 'GET_PROBLEM_RUNS_FULFILLED':
      return {
        ...state,
        ..._.mapValues(action.payload.data, normalizeRun),
      }

    case 'GET_RUN_PROTOCOL_FULFILLED':
      const { runId } = action.meta;
      return {
        ...state,
        [runId]: {
          ...state[runId],
          protocol: normalizeProtocol(action.payload.data),
        }
      }

    case 'WEBSOCKET_GET_RUNS':
      return {
        ...state,
        ..._.mapValues(action.payload, normalizeRun),
      }
  }

  return state;
}
