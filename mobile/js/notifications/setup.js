/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import {
  PermissionsAndroid,
  Platform,
} from 'react-native';
import PushNotification from 'react-native-push-notification';
import moment from 'moment';
import {
  intlShape,
} from 'react-intl';
import { constructIntl } from 'dancedeets-common/js/intl';
import type { TokenRegistration } from '../store/track';
import { setupMixpanelToken } from '../store/track';
import {
  saveToken,
  event as fetchEvent,
} from '../api/dancedeets';
import type { Event } from 'dancedeets-common/js/events/models';
import { purpleColors } from '../Colors';
import {
  navigatePush,
  navigatePop,
  appNavigateToEvent,
  selectTab,
} from '../actions';
import { time as timeFormat } from '../formats';
import {
  PreferenceNames,
  getPreference,
} from './prefs';
import { getCurrentLocale } from '../locale';

let globalHandler = null;

function hashCode(s: string) {
  let hash = 0;
  if (s.length === 0) {
    return hash;
  }
  for (let i = 0; i < s.length; i += 1) {
    const char = s.charCodeAt(i);
    /* eslint-disable no-bitwise */
    hash = ((hash << 5) - hash) + char;
    hash &= hash; // Convert to 32bit integer
    /* eslint-enable no-bitwise */
  }
  return hash;
}

class Handler {
  dispatch: any;
  intl: intlShape;

  constructor(dispatch, intl) {
    this.dispatch = dispatch;
    this.intl = intl;
    (this: any).receivedNotification = this.receivedNotification.bind(this);
  }

  async shouldVibrate() {
    const vibratePermission = await PermissionsAndroid.checkPermission('android.permission.VIBRATE');
    const platformSupportsDefaultVibration = Platform.OS === 'ios' || Platform.Version >= 18;
    const vibratePreference = await getPreference(PreferenceNames.vibration, true);
    const vibrate = (vibratePermission || platformSupportsDefaultVibration) && vibratePreference;
    return vibrate;
  }

  async sendUpcomingEventReminder(event: Event) {
    // TODO: Download larger flyer bitmaps (2:1 ish ratio) to display in the LargeIcon
    // TODO: Set CATEGORY_EVENT
    // TODO: We can add actions, but we can't add icons or make them be ACTION_VIEW mapUrl actions or have icons...
    // TODO: Make this notification expire after the end date of the event:
    // http://stackoverflow.com/questions/23874203/create-an-android-notification-with-expiration-date

    const start = moment(event.start_time, moment.ISO_8601);
    const eventTime = this.intl.formatTime(start.toDate(), timeFormat);
    const eventLocation = event.venue.name;
    const notificationTitle = event.name;
    const notificationMessage = `${eventTime} @ ${eventLocation}`;
    const notificationExpandedText = event.description;

    const vibrate = await this.shouldVibrate();
    const playSound = await getPreference(PreferenceNames.sounds, true);
    PushNotification.localNotification({
      /* Android Only Properties */
      id: hashCode(`upcoming:${event.id}`).toString(), // (optional) Valid unique 32 bit integer specified as string. default: Autogenerated Unique ID
      // ticker: "My Notification Ticker", // (optional) used for accessibility
      autoCancel: true, // (optional) default: true
      // TODO:largeIcon: 'eventFlyerimageBitmap',
      smallIcon: 'ic_penguin_head_outline', // (optional) default: "ic_notification" with fallback for "ic_launcher"
      bigText: notificationExpandedText, // (optional) default: "message" prop
      subText: 'Open Event', // (optional) default: none
      color: purpleColors[2], // (optional) default: system default
      vibrate, // (optional) default: true
      // vibration: 300, // vibration length in milliseconds, ignored if vibrate=false, default: 1000
      tag: 'upcoming_email', // (optional) add tag to message
      group: 'upcoming_email', // (optional) add message to group on watch
      ongoing: false, // (optional) set whether this is an "ongoing" notification

      /* iOS only properties */
      // alertAction: // (optional) default: view
      // category: // (optional) default: null
      // userInfo: // (optional) default: null (object containing additional notification data)

      /* iOS and Android properties */
      title: notificationTitle, // (optional, for iOS this is only used in apple watch, the title will be the app name on other iOS devices)
      message: notificationMessage, // (required)
      playSound, // (optional) default: true
      soundName: 'happening', // (optional) Sound to play when the notification is shown. Value of 'default' plays the default sound. It can be set to a custom sound such as 'android.resource://com.xyz/raw/my_sound'. It will look for the 'my_sound' audio file in 'res/raw' directory and play it. default: 'default' (default sound is played)
      // number: '10', // (optional) Valid 32 bit integer specified as string. default: none (Cannot be zero)

      /* These are passed-through, for when this notification is then opened in-app */
      openedEventId: event.id,
    });
  }

  async receivedNotification(notification: any) {
    /*
      collapse_key: "do_not_collapse"
      foreground: true
      google.message_id: "0:1474442091773929%85df5223f9fd7ecd"
      google.sent_time: 1474442091764
      id: "1814580795"
      mp_campaign_id: "1459430"
      mp_message: "test"
      test: "1"
      userInteraction: false
    */
    console.log('NOTIFICATION:', notification);
    if (notification.userInteraction) {
      if (notification.openedEventId) {
        console.log('OPENED ', notification.openedEventId);
        const notificationEvent = await fetchEvent(notification.openedEventId);
        this.dispatch(appNavigateToEvent(notificationEvent));
      }
    } else if (notification.notification_type === 'EVENT_REMINDER') {
      const notificationsEnabled = await getPreference(PreferenceNames.overall, true);
      if (notificationsEnabled) {
        const notificationEvent = await fetchEvent(notification.event_id);
        this.sendUpcomingEventReminder(notificationEvent);
      }
    }
  }
}

function init() {
  const intl = constructIntl(getCurrentLocale());
  globalHandler = new Handler(null, intl);
  let lastTokenRegistration = null;

  PushNotification.configure({
    async onRegister(tokenRegistration: TokenRegistration) {
      // Don't re-process if we've already already recorded this token
      if (lastTokenRegistration === tokenRegistration.token) {
        return;
      }
      lastTokenRegistration = tokenRegistration.token;
      setupMixpanelToken(tokenRegistration);
      await saveToken(tokenRegistration);
    },

    onNotification: globalHandler.receivedNotification,

      // ANDROID ONLY: GCM Sender ID (optional - not required for local notifications, but is need to receive remote push notifications)
    senderID: '911140565156',

      // IOS ONLY (optional): default: all - Permissions to register.
    permissions: {
      alert: true,
      badge: true,
      sound: true,
    },

      // Should the initial notification be popped automatically
      // default: true
    popInitialNotification: false,

      /**
        * (optional) default: true
        * - Specified if permissions (ios) and token (android and ios) will requested or not,
        * - if not, you must call PushNotificationsHandler.requestPermissions() later
        */
    requestPermissions: Platform.OS === 'android',
  });
}

// Initialize ASAP here, so that the background listener service can process/handle notifications
// This gets called repeatedly in DEV mode, so don't use popInitialNotification.
init();

// Later, call setup() once we have a proper dispatch, that gets used when our App UI is initialized,
// so our opened notifications can script the UI properly.
// We use popInitialNotification here, to process the incoming app-opening intents as if we received them.
// It doesn't make sense to popInitialNotification on the listener service configuration above.
export function setup(dispatch: Object, intl: intlShape) {
  globalHandler = new Handler(dispatch, intl);
  PushNotification.configure({
    popInitialNotification: true,
    onNotification: globalHandler.receivedNotification,
    requestPermissions: false, // Make sure we don't request permissions on iOS (or anywhere)
  });
}
