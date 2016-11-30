/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import type { Action } from './types';

export function selectTab(tab: string): Action {
  return {
    type: 'TAB_SELECT',
    tab,
  };
}
