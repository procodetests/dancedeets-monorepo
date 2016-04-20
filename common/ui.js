/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */
'use strict';

import React, {
  Image,
  View,
} from 'react-native';

export class ProportionalImage extends React.Component {
  props: {
    originalWidth: number,
    originalHeight: number,
    style?: any,
  };

  state: {
    style: {height: number} | {},
  };

  constructor(props) {
    super(props);
    this.state = {
      style: {}
    };
    (this: any).onLayout = this.onLayout.bind(this);
  }

  onLayout(e: SyntheticEvent) {
    const nativeEvent: any = e.nativeEvent;
    const layout = nativeEvent.layout;
    const aspectRatio = this.props.originalWidth / this.props.originalHeight;
    const measuredHeight = layout.width / aspectRatio;
    const currentHeight = layout.height;

    if (measuredHeight !== currentHeight) {
      this.setState({
        style: {
          height: measuredHeight
        }
      });
    }
  }

  render() {
    // We catch the onLayout in the view, find the size, then resize the child (before it is laid out?)
    return (
      <View
        onLayout={this.onLayout}
        >
        <Image
          {...this.props}
          style={[this.props.style, this.state.style]}
        />
      </View>
    );
  }
}

