/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import React, { PropTypes } from 'react';
import { IntlProvider } from 'react-intl';
import Locale from 'react-native-locale';
import areIntlLocalesSupported from 'intl-locales-supported';
import moment from 'moment';

const defaultLocale = 'en';
const locales = ['en', 'ja', 'fr', 'zh', 'ko'];

const getCurrentLocale = () => {
  const currentLocale = Locale.constants().localeIdentifier.split('_')[0].split('-')[0];
  return locales.indexOf(currentLocale) !== -1
    ? currentLocale
    : defaultLocale;
};

import 'moment/locale/fr';
import 'moment/locale/ja';
import 'moment/locale/zh-tw';
import fr from './messages/fr.json';
import ja from './messages/ja.json';
import zh from './messages/zh.json';
const messages = {
  fr,
  ja,
  zh,
};

// https://github.com/yahoo/intl-locales-supported#usage
if (global.Intl) {
  // Determine if the built-in `Intl` has the locale data we need.
  if (!areIntlLocalesSupported(locales)) {
    // `Intl` exists, but it doesn't have the data we need, so load the
    // polyfill and replace the constructors we need with the polyfill's.
    require('intl');
    Intl.NumberFormat = IntlPolyfill.NumberFormat; // eslint-disable-line no-undef
    Intl.DateTimeFormat = IntlPolyfill.DateTimeFormat; // eslint-disable-line no-undef
  }
} else {
  // No `Intl`, so use and load the polyfill.
  global.Intl = require('intl');
}

export default function intl(Wrapped) {
  class Internationalize extends React.Component {

    render() {
      const currentLocale = getCurrentLocale();
      // Our Locale.contstants().localeIdentifier returns zh-Hant_US.
      // But moment locales are zh-tw (traditional) and zh-cn (simplified).
      // So manually convert the getCurrentLocale() 'zh' to the 'zh-tw' moment needs:
      let momentLocale = currentLocale;
      if (momentLocale === 'zh') {
        momentLocale = 'zh-tw';
      }
      moment.locale(momentLocale);
      return (
        <IntlProvider
          defaultLocale={defaultLocale}
          key={currentLocale} // https://github.com/yahoo/react-intl/issues/234
          locale={currentLocale}
          messages={messages[currentLocale]}
        >
          <Wrapped {...this.props} />
        </IntlProvider>
      );
    }

  }

  return Internationalize;
}
