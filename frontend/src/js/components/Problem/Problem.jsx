import PropTypes from 'prop-types';
import React from 'react';
import ReactDOM from 'react-dom';
import styled from 'styled-components';
import { connect } from 'react-redux';
import { palette } from 'styled-theme';
import * as _ from 'lodash';

import Box from '../../components/utility/Box';
import GroupFilter from '../../components/GroupFilter/GroupFilter';
import Header from '../../components/utility/Header';
import Runs from '../Runs/Runs';
import Sample from './Sample';
import StandingsPane from './StandingsPane';
import SubmissionsPane from './SubmissionsPane';
import SubmitForm from './SubmitForm';
import Tabs, { TabPane } from '../../components/utility/Tabs';
import * as problemActions from '../../actions/problemActions';
import * as submitActions from '../../actions/submitActions';


const ProblemWrapper = styled.div`
  > div {
    height: auto;
  }

  .problemTitle {
    display: flex;
    flex-flow: row nowrap;
    margin: 10px 0 34px 0;
    font-size: 18px;
    color: ${palette('secondary', 0)};
    width: 100%;
    text-align: center;

    i {
      cursor: pointer;
      display: none;
    }
    span { margin: auto; }
  }

  .problemLimits {
    display: flex;
    flex-flow: row wrap;
    justify-content: space-around;
    padding: 10px;

    background: #f8f8f8;
    color: ${palette('other', 13)};
    border-radius: 4px;

    @media (max-width: 575px) {
      flex-flow: column nowrap;
    }
  }

  .problemStatement {
    text-align: left;
    color: ${palette('other', 7)};

    .legend {
      p { margin-bottom: 34px; }
    }

    div {
      margin-bottom: 34px;

      .section-title {
        width: 100%;
        margin-bottom: 20px;

        display: flex;
        align-items: center;

        font-size: 19px;
        font-weight: 500;
        color: ${palette('secondary', 2)};
        white-space: nowrap;

        &:before {
          content: '';
          width: 5px;
          height: 40px;
          background: ${palette('secondary', 3)};
          display: flex;
          margin-right: 15px;
        }

        &:after {
          content: '';
          width: 100%;
          height: 1px;
          background: ${palette('secondary', 3)};
          display: flex;
          margin-left: 15px;
        }
      }
    }
  }

  .problemSamples {
    > *:not(:last-child) { margin-bottom: 34px; }
  }

  .tabStatement > * { margin-bottom: 30px; }
`;


export class Problem extends React.Component {
  static propTypes = {
    problemId: PropTypes.number.isRequired,
    statementId: PropTypes.number,
    onTabChange: PropTypes.func,
  };

  constructor(props) {
    super(props);

    this.problemId = this.props.problemId;

    this.fetchProblem = this.fetchProblem.bind(this);
    this.fetchProblemRuns = this.fetchProblemRuns.bind(this);
    this.fetchProblem();
    this.fetchProblemRuns();
  }

  componentDidUpdate(prevProps) {
    const { problemId } = this.props;
    const { problemId: prevProblemId } = prevProps;
    this.problemId = problemId;

    if (problemId !== prevProblemId) {
      this.fetchProblem();
      this.fetchProblemRuns();
    }
  }

  fetchProblem() {
    const { problemId } = this.props;
    this.props.dispatch(problemActions.fetchProblem(problemId));
  }

  fetchProblemRuns() {
    const { problemId, statementId } = this.props;
    this.props.dispatch(problemActions.fetchProblemRuns(problemId, statementId));
    this.props.dispatch(submitActions.fetchUserSubmits());
  }

  render() {
    const { problemId, userId } = this.props;
    const {
      name: problemTitle,
      content: problemStatement,
      sample_tests_json: problemSamples,
      timelimit: problemTimeLimit,
      memorylimit: problemMemoryLimit,
      show_limits: problemShowLimits,
    } = _.get(this.props.problems, `[${problemId}].data`, {});
    const problemRuns = _.get(this.props.problems[problemId], 'runs', []);
    const problemSubmits = _.get(this.props.problems[problemId], 'submits', []);

    const additionalTabsProps = (this.problemId !== problemId)
      ? { activeKey: 'statement' }
      : {};

    return (
      <ProblemWrapper>
        <Box>
          <div className="problemTitle">
            <span>Задача №{problemId}. {problemTitle}</span>
          </div>

          <Tabs
            defaultActiveKey="statement"
            style={{ textAlign: 'center' }}
            onChange={this.props.onTabChange}
            {...additionalTabsProps}
          >
            <TabPane className="tabStatement" tab="Условие" key="statement">
              {
                problemShowLimits
                ? (
                  <div className="problemLimits">
                    <div>Ограничение по времени, сек: {problemTimeLimit}</div>
                    <div>Ограничение по памяти, мегабайт: {problemMemoryLimit / 1024 / 1024}</div>
                  </div>
                ) : null
              }
              <div
                className="problemStatement"
                dangerouslySetInnerHTML={{ __html: problemStatement }}
                // ref={(node) => window.MathJax.Hub.Queue(['Typeset', window.MathJax.Hub, node])}
              />
              <Header style={{ marginBottom: 30 }}>Примеры</Header>
              <div className="problemSamples">
                { _.map(problemSamples, ({input, correct}, id) => <Sample key={id} input={input} correct={correct}/>) }
              </div>
              <SubmitForm problemId={problemId} />
              <Runs
                userId={userId}
                runIds={problemRuns}
                submitIds={problemSubmits}
                fetchRuns={this.fetchProblemRuns}
              />
            </TabPane>
            <TabPane tab="Результаты" key="standings">
              <StandingsPane problemId={problemId} />
            </TabPane>
            <TabPane tab="Посылки FIXME" key="runs">
              <SubmissionsPane problemId={problemId} runIds={problemRuns} />
            </TabPane>
            <TabPane tab="Решение" key="solution" disabled />
            <TabPane tab="Темы и источники" key="sources" disabled />
          </Tabs>
        </Box>
      </ProblemWrapper>
    );
  }
}

export default connect(state => ({
  problems: state.problems,
  userId: state.user.id,
}))(Problem);
