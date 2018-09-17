import PropTypes from 'prop-types';
import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { palette } from 'styled-theme';

import { TypeContestIcon } from '../../components/Icon';
import SectionModule from './Modules';


const SectionWrapper = styled.div`
  padding: 25px 35px;

  .sectionHeader {
    text-align: left;

    .sectionTitle {
      color: ${palette('other', 17)};
      font-size: 18px;
      display: inline;
      margin-right: 20px;
    }

    .sectionMore {
      color: ${palette('other', 13)};
      font-size: 12px;
      display: inline;
      cursor: pointer;
      user-select: none;
      white-space: nowrap;
    }

    .sectionDescription {
      color: ${palette('other', 13)};
      font-size: 12px;
      margin: 10px 0 15px 0;
    }
  }

  .sectionModules {
    margin-top: 15px;

    .sectionModule {
      display: flex;

      i { margin-top: 2px; }

      .sectionModuleName {
        color: ${palette('other', 6)};
        font-size: 15px;
        font-weight: bold;
        margin: 0 10px;
        text-align: left;
      }
    }
  }

  @media (max-width: 720px) {
    padding: 25px 10px;
  }
`;


class SectionTitle extends React.Component {
  static propTypes = {
    title: PropTypes.string.isRequired,
  };

  static shortLength = 70;

  constructor() {
    super();
    this.state = { shorten: true };
  }

  get titleIsLong() {
    return this.props.title.length > SectionTitle.shortLength;
  }

  get shortenedTitle() {
    return this.props.title.substring(0, SectionTitle.shortLength) + '...';
  }

  render() {
    let { title } = this.props;
    const { shorten } = this.state;

    return (
      <div className="sectionHeader">
        <div className="sectionTitle">{shorten && this.titleIsLong ? this.shortenedTitle : title}</div>
        <div
          className="sectionMore"
          onClick={() => this.setState({ shorten: !shorten })}
        >
          {
            this.titleIsLong
            ? (shorten ? 'Развернуть' : 'Свернуть')
            : null
          }
        </div>
      </div>
    );
  }
}


export default class Section extends React.Component {
  render() {
    const {
      modules,
      section,
      sequence,
      summary,
    } = this.props.section;

    const sectionModules = _.chain(sequence)
      .filter(moduleId => _.has(modules, moduleId))
      .map(moduleId => modules[moduleId])
      .map(({ id, instance, type }) => <SectionModule instance={instance} key={id} type={type} />)
      .value();

    return (
      <SectionWrapper>
        <SectionTitle title={`${section}. ${summary}`} />
        <div className="sectionModules">
          {sectionModules}
        </div>
      </SectionWrapper>
    );
  }
}