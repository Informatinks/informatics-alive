const initialState = {};


const updateQueuePositions = (state, lastGetId) => {
  return _.chain(state)
    .pickBy(submit => submit.id > lastGetId)
    .mapValues(submit => ({
      ...submit,
      queuePosition: submit.id - lastGetId,
    }))
    .value();
}


export default function reduce(state=initialState, action) {
  let lastGetId, submit, submits;
  switch (action.type) {
    case 'GET_USER_SUBMITS_FULFILLED':
      ({ lastGetId, submits } = action.payload.data);
      return updateQueuePositions({...state, ...submits}, lastGetId);

    case 'POST_PROBLEM_SUBMIT_FULFILLED':
      ({ lastGetId, submit } = action.payload.data);
      return updateQueuePositions({...state, [submit.id]: submit}, lastGetId);

    case 'UPDATE_QUEUE_STATUS':
      ({ lastGetId } = action.payload);
      return updateQueuePositions({...state}, lastGetId);
  }
  return state;
}
