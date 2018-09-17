import React from 'react';
import PropTypes from 'prop-types';

import Runs from '../Runs/Runs';


export default class SubmissionsPane extends React.Component {
  static propTypes = {
    runIds: PropTypes.array.isRequired,
  };

  render() {
    return (
      <Runs
        runIds={this.props.runIds}
        showRows={15}
        showUserInfo={true}
      />
    );
  };
}
