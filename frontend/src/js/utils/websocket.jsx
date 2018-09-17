import camelcaseKeys from 'camelcase-keys';
import io from 'socket.io-client';

import * as runActions from '../actions/runActions';
import * as submitActions from '../actions/submitActions';


const prepareData = data => camelcaseKeys(data, {deep: true});


export default class Socket {
  constructor(url, dispatch) {
    this.dispatch = dispatch;
    this.socket = io(url, { transports: ['websocket', 'polling'] });

    this.socket.on('connect', () => this.onConnect());
    this.socket.on('disconnect', () => this.onDisconnect());

    this.socket.on('QUEUE_STATUS', data => this.onQueueStatus(data));
    this.socket.on('RUNS_FETCH', data => this.onRunsFetch(data));
    this.socket.on('SUBMIT_ERROR', data => this.onSubmitError(data));
    this.socket.on('SUBMIT_SUCCESS', data => this.onSubmitSuccess(data));
  }

  onConnect() {}
  onDisconnect() {}

  onQueueStatus(data) {
    const { lastGetId } = prepareData(data);
    this.dispatch(submitActions.updateQueueStatus(lastGetId));
  }
  onRunsFetch(data) {}
  onSubmitError(data) {}
  onSubmitSuccess(data) {
    const { run } = prepareData(data);
    this.dispatch(runActions.websocketGetRuns({[run.id]: run}));
  }
}
