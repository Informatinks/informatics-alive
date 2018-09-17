import axios from '../utils/axios';


export function fetchRunProtocol(runId, ejudgeContestId, ejudgeRunId) {
  return (dispatch) => {
    const url = `/protocol/get_v2/${ejudgeContestId}/${ejudgeRunId}`;

    return dispatch({
      type: 'GET_RUN_PROTOCOL',
      payload: axios.get(
        url,
        {
          withCredentials: true,
          camelcaseKeys: true,
        },
      ),
      meta: { runId },
    });
  };
}


export function websocketGetRuns(runs) {
  return (dispatch) => {
    return dispatch({
      type: 'WEBSOCKET_GET_RUNS',
      payload: runs,
    })
  }
}
