import striptags from 'striptags';
import _ from 'lodash';


const normalizeSection = (section) => ({
  ...section,
  summary: striptags(section.summary),
  modules: _.mapKeys(section.modules, module => module.id),
});


const normalizeCourse = (course) => {
  const { sections } = course;
  return {
    ...course,
    sections: _.map(sections, normalizeSection),
  };
};


const initialState = {};

export default function reduce(state = initialState, action) {
  let courseId;
  switch (action.type) {
    case 'GET_COURSE_FULFILLED':
      courseId = action.payload.data.id;
      return {
        ...state,
        [courseId]: normalizeCourse(action.payload.data),
      };
  }
  return state;
}
