import PropTypes from 'prop-types';
import React from 'react';
import styled from 'styled-components';
import { connect } from 'react-redux';
import { Table } from 'antd';
import * as _ from 'lodash';

import Button from '../utility/Button';
import CodeMirror from '../../components/utility/CodeMirror';
import Modal from '../utility/Modal';
import SamplesProtocolPane from './SamplesProtocolPane';
import Status from './Status';
import Tabs, { TabPane } from '../utility/Tabs';
import Tooltip from '../../components/utility/Tooltip';
import { LANGUAGES } from '../../constants';
import * as runActions from '../../actions/runActions';


const testsColumns = [
  {
    dataIndex: 'key',
    key: 'key',
    title: '#',
    className: 'protocolColumnId',
  },
  {
    dataIndex: 'status',
    key: 'status',
    title: 'Статус',
    render: status => <Status status={status}/>,
    className: 'protocolColumnStatus',
  },
  {
    dataIndex: 'time',
    key: 'time',
    title: <Tooltip title="Время работы">🕓</Tooltip>,
    className: 'protocolColumnTime',
  },
  {
    dataIndex: 'realTime',
    key: 'realTime',
    title: <Tooltip title="Астрономическое время работы">👩‍🚀</Tooltip>,
    className: 'protocolColumnRealTime',
  },
  {
    dataIndex: 'maxMemoryUsed',
    key: 'maxMemoryUsed',
    title: 'Используемая память',
    className: 'protocolColumnMemoryUsed',
  },
];


const ProtocolButtonModalContentWrapper = styled.div`
  .ant-table td {
    white-space: nowrap;
  }

  .ant-table-content { overflow-x: auto; }

  .protocolColumnId {
    width: 1px;
    white-space: nowrap;
  }

  .protocolColumnStatus,
  .protocolColumnMemoryUsed {
    white-space: nowrap;
    text-align: center;
  }
  .protocolColumnTime,
  .protocolColumnRealTime {
    white-space: nowrap;
    text-align: center;
    width: 1px;
  }

  @media (max-width: 575px) {
    .ant-tabs {
      margin-top: 20px;
    }
  }
`;

export class ProtocolButton extends React.Component {
  static propTypes = {
    runId: PropTypes.number,
    runs: PropTypes.object.isRequired,
    user: PropTypes.object.isRequired,
  };

  constructor() {
    super();

    this.state = {
      visible: false,
    };

    this.showModal = this.showModal.bind(this);
  }

  showModal() {
    const { runId, runs } = this.props;
    const { ejudgeContestId, ejudgeRunId } = runs[runId];
    this.props.dispatch(runActions.fetchRunProtocol(runId, ejudgeContestId, ejudgeRunId));

    this.setState({...this.state, visible: true});
  }

  render() {
    const { runId, runs, user } = this.props;
    const run = runs[runId] || {};

    const { languageId, protocol, source, userId } = run;
    const { compilerOutput, tests } = protocol || {};

    const authored = userId === user.id;

    const testsData = _.map(tests, (value, key) => ({
      key,
      status: value.status,
      time: (value.time / 1000).toFixed(3),
      realTime: (value.realTime / 1000).toFixed(3),
      maxMemoryUsed: value.maxMemoryUsed,
    }));

    const samples = _.pickBy(tests, test => _.has(test, 'input'));

    return (
      <div>
        <Modal
          visible={this.state.visible}
          footer={null}
          mask={false}
          onCancel={() => this.setState({...this.state, visible: false})}
          width={720}
          destroyOnClose={true}
        >
          <ProtocolButtonModalContentWrapper>
            <Tabs>
            <TabPane key="source" tab="Код">
              <CodeMirror
                value={source}
                options={{
                  lineNumbers: true,
                  readOnly: true,
                  tabSize: 4,
                  mode: _.get(LANGUAGES, `[${languageId}].mime`, ''),
                }}
              />
            </TabPane>
            <TabPane key="protocol" tab="Протокол">
              <Table
                dataSource={testsData}
                columns={testsColumns}
                size="small"
                pagination={false}
              />
              { compilerOutput
                ? (
                  <div className="compilerOutput">
                    <div>Сообщение компилятора:</div>
                    <div>{compilerOutput}</div>
                  </div>
                )
                : null
              }
            </TabPane>
            <TabPane key="samplesProtocol" tab="Тесты из условия">
              <SamplesProtocolPane samples={samples}/>
            </TabPane>
            {/*<TabPane key="fullProtocol" tab="Полный протокол">1</TabPane>*/}
          </Tabs>
          </ProtocolButtonModalContentWrapper>
        </Modal>
        <Button
          type="secondary"
          size="small"
          style={{ padding: 0, display: 'flex' }}
          onClick={this.showModal}
          disabled={!authored || typeof runId === 'undefined'}
        >
          <i className="material-icons">keyboard_arrow_right</i>
        </Button>
      </div>
    );
  }
}

export default connect(state => ({
  runs: state.runs,
  user: state.user,
}))(ProtocolButton);
