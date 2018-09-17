import { combineReducers } from 'redux';
import { reducer as form } from 'redux-form';

import context from './contextReducer';
import courses from './coursesReducer';
import group from './groupReducer';
import problems from './problemsReducer';
import routing from './routingReducer';
import runs from './runsReducer';
import statements from './statementsReducer';
import submits from './submitsReducer';
import ui from './uiReducer';
import user from './userReducer';
import users from './usersReducer';


export default combineReducers({
  context,
  courses,
  group,
  form,
  problems,
  routing,
  runs,
  statements,
  submits,
  ui,
  user,
  users,
})
