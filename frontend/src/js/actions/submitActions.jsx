import axios from '../utils/axios';


export function fetchUserSubmits() {
  return (dispatch) => {
    return dispatch({
      type: 'GET_USER_SUBMITS',
      payload: axios.get(
        '/submit',
        {
          camelcaseKeys: true,
        }
      ),
    });
  };
}


export function updateQueueStatus(lastGetId) {
  return (dispatch) => {
    return dispatch({
      type: 'UPDATE_QUEUE_STATUS',
      payload: { lastGetId },
    });
  }
}
