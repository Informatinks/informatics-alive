import axios from '../utils/axios';


export function fetchCourse(courseId) {
  return (dispatch) => {
    const url = `/course/${courseId}`;

    return dispatch({
      type: 'GET_COURSE',
      payload: axios.get(url, { camelcaseKeys: true }),
    })
  }
}