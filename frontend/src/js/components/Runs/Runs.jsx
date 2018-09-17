import PropTypes from 'prop-types';
import React from 'react';
import styled from 'styled-components';
import { Icon, Table } from 'antd'
import { connect } from 'react-redux';
import { palette } from 'styled-theme';
import * as _ from 'lodash';

import Button from '../../components/utility/Button';
import ProtocolButton from './ProtocolButton';
import Status from './Status';
import moment from '../../utils/moment';
import { LANGUAGES } from '../../constants';
import * as problemActions from '../../actions/problemActions';


const runsColumns = (fetchRuns, userColumn) => [
  {
    dataIndex: 'status',
    key: 'status',
    render: status => <Status status={status}/>,
    className: 'runsColumnStatus',
  },
  {
    dataIndex: 'id',
    key: 'id',
    title: '#',
    className: 'runsColumnId',
  },
  (userColumn
    ? {
      dataIndex: 'user',
      key: 'user',
      title: 'Участник',
      render: user => `${user.firstname} ${user.lastname}`,
    }
    : {}
  ),
  {
    dataIndex: 'createTime',
    key: 'createTime',
    title: 'Дата',
    className: 'runsColumnDate',
    render: createTime => createTime
      ? moment(createTime).calendar(null, {
        sameDay: 'HH:mm',
        lastDay: '[Вчера в] HH:mm',
        lastWeek: 'DD.MM.YYYY HH:mm',
        sameElse: 'DD.MM.YYYY HH:mm',
      })
      : '—',
  },
  {
    dataIndex: 'languageId',
    key: 'languageId',
    title: 'Язык',
    className: 'runsColumnLanguage',
    render: languageId => _.get(LANGUAGES, `[${languageId}].name`, ''),
  },
  {
    dataIndex: 'score',
    key: 'score',
    title: 'Баллы',
    className: 'runsColumnScore',
  },
  {
    className: 'refreshBtn',
    key: 'refresh',
    title: (
      <i
        onClick={fetchRuns}
        className="material-icons"
      >
        sync
      </i>
    ),
    render: row => <ProtocolButton runId={row.runId} />
  },
];


const RunsWrapper = styled.div`
  .ant-table-thead > tr > th {
    background: ${palette('other', 15)};
    color: rgba(33, 37, 41,0.5);
    font-weight: normal;
    font-size: 12px;
  }
  .ant-table-content { overflow-x: auto; }

  .runsColumnScore,
  .refreshBtn {
    width: 1px;
    text-align: center;
    white-space: nowrap;
  }
  .runsColumnId,
  .runsColumnStatus,
  .runsColumnDate,
  .runsColumnLanguage {
    text-align: center;
    white-space: nowrap;
  }

  .buttons {
    display: flex;
    flex-flow: row wrap;
    justify-content: space-between;
    margin-top: 10px;

    @media (max-width: 767px) { display: none; }
  }

  .refreshBtn {
    i { cursor: pointer; }
    span { display: flex; }
  }
`;

export class Runs extends React.Component {
  static contextTypes = {
    statementId: PropTypes.number,
  };

  static propTypes = {
    runIds: PropTypes.array.isRequired,
    submitIds: PropTypes.array,
    userId: PropTypes.number,
    showUserInfo: PropTypes.bool,
    showRows: PropTypes.number,
    fetchRuns: PropTypes.func,
    runs: PropTypes.object.isRequired,
    windowWidth: PropTypes.number.isRequired,
  };

  static defaultProps = {
    submitIds: [],
    showUserInfo: false,
    showRows: 5,
  };

  constructor() {
    super();

    this.state = {
      showMore: false,
    };

    this.toggleShowMore = this.toggleShowMore.bind(this);
  }

  toggleShowMore() {
    this.setState({
      ...this.state,
      showMore: !this.state.showMore,
    })
  }

  render() {
    const { showMore } = this.state;
    const {
      fetchRuns,
      runIds,
      runs,
      showRows,
      showUserInfo,
      submitIds,
      submits,
      user,
      userId,
      users,
      windowWidth,
    } = this.props;

    const submitsData = _.chain(submits)
      .pick(submitIds)
      .filter(submit => typeof submit === 'undefined' || submit.userId === userId)
      .map(submit => ({
        ...submit,
        id: `${submit.queuePosition} в очереди`,
        key: 'submit' + submit.id,
        score: '—',
        status: '1000',
        submitId: submit.id,
        user: users[submit.userId],
      }))
      .orderBy(['id'], ['desc'])
      .value();

    const runsData = _.chain(runs)
      .pick(runIds)
      .filter(run => typeof userId === 'undefined' || run.userId === userId)
      .map(run => ({
        ...run,
        key: 'run' + run.id,
        runId: run.id,
        user: users[run.userId],
      }))
      .orderBy(['createTime'], ['desc'])
      .value();

    const data = _.concat(submitsData, runsData);

    return (
      <RunsWrapper>
        <Table
          columns={runsColumns(fetchRuns, showUserInfo)}
          dataSource={ showMore || windowWidth < 768 ? data : data.slice(0, showRows) }
          pagination={false}
          scroll={{ x: 600 }}
        />
        <div className="buttons">
          <Button
            type="secondary"
            onClick={this.toggleShowMore}
            disabled={data.length <= showRows}
          >
            Показать еще
          </Button>
          <Button type="secondary" disabled>Архив посылок</Button>
        </div>
      </RunsWrapper>
    );
  }
}

export default connect(state => ({
  runs: state.runs,
  submits: state.submits,
  user: state.user,
  users: state.users,
  windowWidth: state.ui.width,
}))(Runs);
