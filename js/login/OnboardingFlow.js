/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import {
  Linking
} from 'react-native';
import { connect } from 'react-redux';
import TutorialScreen from './TutorialScreen';
import NoLoginScreen from './NoLoginScreen';
import { loginButtonPressed } from './logic';
import { track } from '../store/track';

const mapDispatchToProps = (dispatch) => {
  return {
    onLogin: (e) => loginButtonPressed(dispatch),
  };
};

type ScreenState = 'CAROUSEL' | 'NO_LOGIN';

class OnboardingFlow extends React.Component {
  props: {
    onLogin: () => void,
  };

  state: {
    screen: ScreenState,
  };

  constructor(props) {
    super(props);
    this.state = {
      screen: 'CAROUSEL',
    };
    (this: any).onDontWantLoginPressed = this.onDontWantLoginPressed.bind(this);
    (this: any).onOpenWebsite = this.onOpenWebsite.bind(this);
  }

  onDontWantLoginPressed() {
    track('Login - Without Facebook');
    this.setState({...this.state, screen: 'NO_LOGIN'});
  }

  onOpenWebsite() {
    track('Login - Use Website');
    Linking.openURL('http://www.dancedeets.com/').catch(err => console.error('Error opening dancedeets.com:', err));
  }

  render() {
    if (this.state.screen === 'CAROUSEL') {
      return <TutorialScreen
        onLogin={this.props.onLogin}
        onNoLogin={this.onDontWantLoginPressed}
      />;
    } else if (this.state.screen === 'NO_LOGIN') {
      return <NoLoginScreen
        onLogin={this.props.onLogin}
        onNoLogin={this.onOpenWebsite}
        />;
    }
  }
}

export default connect(
    null,
    mapDispatchToProps
)(OnboardingFlow);
