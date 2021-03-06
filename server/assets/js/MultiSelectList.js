/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';

type SelectProps = {
  toggleState: () => void,
  active: boolean,
  item: string,
  itemRenderer?: (item: string) => React.Node,
};

export class SelectButton extends React.Component<SelectProps> {
  _button: ?HTMLButtonElement;

  constructor(props: SelectProps) {
    super(props);
    (this: any).toggleState = this.toggleState.bind(this);
  }

  toggleState(e: SyntheticMouseEvent<>) {
    this.props.toggleState();
    if (this._button) {
      this._button.blur();
    }
    e.preventDefault();
  }

  render() {
    let extraClass = '';
    if (this.props.active) {
      extraClass = 'active';
    }
    const contents = this.props.itemRenderer
      ? this.props.itemRenderer(this.props.item)
      : this.props.item;

    return (
      <button
        type="button"
        className={`btn btn-default btn-sm ${extraClass}`}
        ref={x => {
          this._button = x;
        }}
        onClick={this.toggleState}
      >
        {contents}
      </button>
    );
  }
}

export type MultiSelectState = { [item: string]: boolean };

export function generateUniformState(list: Array<string>, value: boolean) {
  const newState = {};
  list.forEach(x => {
    newState[x] = value;
  });
  return newState;
}

export function caseInsensitiveSort(a: string, b: string) {
  return a.toLowerCase().localeCompare(b.toLowerCase());
}

type State = { [item: string]: boolean };

export function getSelected(state: State) {
  return Object.keys(state)
    .filter(x => state[x])
    .sort(caseInsensitiveSort);
}

export function isAllSelected(state: State) {
  return getSelected(state).length === Object.keys(state).length;
}

type MultiSelectProps = {
  list: Array<string>,
  selected: MultiSelectState,
  itemRenderer?: (item: string) => React.Node,
  onChange: (state: MultiSelectState) => void,
};

export class MultiSelectList extends React.Component<MultiSelectProps> {
  constructor(props: MultiSelectProps) {
    super(props);
    (this: any).toggleItem = this.toggleItem.bind(this);
    (this: any).setAll = this.setAll.bind(this);
  }

  setAll() {
    this.changedState(generateUniformState(this.props.list, true));
  }

  changedState(newState: State) {
    this.props.onChange(newState);
  }

  toggleItem(item: string) {
    if (isAllSelected(this.props.selected)) {
      const newState = generateUniformState(this.props.list, false);
      newState[item] = true;
      this.changedState(newState);
    } else {
      const newState = {
        ...this.props.selected,
        [item]: !this.props.selected[item],
      };
      if (getSelected(newState).length) {
        this.changedState(newState);
      } else {
        this.changedState(generateUniformState(this.props.list, true));
      }
    }
  }

  render() {
    const options = [];
    const allSelected = isAllSelected(this.props.selected);
    options.push(
      <SelectButton
        key="All"
        item="All"
        active={allSelected}
        toggleState={this.setAll}
      />
    );
    const value = getSelected(this.props.selected);
    this.props.list.forEach((item, i) => {
      const selected = !allSelected && value.indexOf(item) !== -1;
      options.push(
        <SelectButton
          key={item}
          item={item}
          active={selected}
          toggleState={() => this.toggleItem(item)}
          itemRenderer={this.props.itemRenderer}
        />
      );
    });
    return (
      <div className="btn-group" role="group">
        {options}
      </div>
    );
  }
}
