import * as _ from 'lodash';


const initialState = {};


export default function reduce(state=initialState, action) {
  switch (action.type) {
    case 'GET_PROBLEM_RUNS_FULFILLED':
      return {
        ...state,
        ..._.chain(action.payload.data)
          .map(run => run.user)
          .mapKeys(user => user.id)
          .value(),
      }
  }

  return state;
}
