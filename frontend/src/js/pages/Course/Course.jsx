import React from 'react';
import { palette } from 'styled-theme';
import { connect } from 'react-redux';
import { Layout, Spin } from 'antd';
import _ from 'lodash';


import Tabs, { TabPane } from '../../components/utility/Tabs';
import MainContentWrapper from '../../components/utility/MainContentWrapper';
import Box from '../../components/utility/Box';
import BackButton from '../../components/BackButton'
import Section from './Section';
import * as courseActions from '../../actions/courseActions';


const CoursePageWrapper = MainContentWrapper.extend`
  .courseHeader {
    position: relative;
    text-align: center;

    .courseBackBtn {
      position: absolute;
      z-index: 1;
      left: 0;
      top: 0;
      opacity: 0.5;
    }

    .courseTitle {
      font-size: 20px;
      color: ${palette('other', 16)};
    }
  }

  @media (max-width: 1279px) {
    .courseBackBtn { display: none; }
  }
`;


export class Course extends React.Component {
  constructor() {
    super();

    this.state = { spin: true };
  }

  get courseId() {
    return this.props.match.params.courseId;
  }

  get course() {
    return this.props.courses[this.courseId];
  }

  componentDidMount() {
    this.props.dispatch(courseActions.fetchCourse(this.courseId))
      .then(() => this.setState({...this.state, spin: false}));
  }

  render() {
    const { spin } = this.state;

    if (spin) {
      return <Spin />;
    }

    const { shortName, sections } = this.course;
    const sectionComponents = _.map(sections, section => <Section key={section.id} section={section} />);

    return (
      <CoursePageWrapper>
        <Layout>
          <Box>
            <div className="courseHeader">
              <BackButton className="courseBackBtn" />
              <div className="courseTitle">{shortName}</div>
            </div>
            <Tabs style={{ textAlign: 'center' }}>
              <TabPane tab="Содержание" key="content">
                {sectionComponents}
              </TabPane>
              <TabPane tab="Результаты" key="results" disabled></TabPane>
            </Tabs>
          </Box>
        </Layout>
      </CoursePageWrapper>
    );
  }
}

export default connect(state => ({
  courses: state.courses,
}))(Course);
