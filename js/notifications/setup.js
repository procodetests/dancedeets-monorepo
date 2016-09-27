/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import {
  PermissionsAndroid,
  Platform,
} from 'react-native';
import PushNotification from 'react-native-push-notification';
import type { TokenRegistration } from '../store/track';
import { setupMixpanelToken } from '../store/track';
import {
  saveToken,
  event as fetchEvent,
} from '../api/dancedeets';
import type {Event} from '../events/models';
import { purpleColors } from '../Colors';
import {
  navigatePush,
  navigatePop,
  selectTab,
} from '../actions';

function hashCode(s: string) {
  let hash = 0;
  if (s.length == 0) {
    return hash;
  }
  for (let i = 0; i < s.length; i++) {
    const char = s.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return hash;
}

class Handler {
  dispatch: any;

  constructor(dispatch) {
    this.dispatch = dispatch;
    (this: any).receivedNotification = this.receivedNotification.bind(this);
  }

  async sendUpcomingEventReminder(event: Event) {
    // TODO: Limitations of PushNotification:
    // TODO: Download larger flyer bitmaps (2:1 ish ratio) to display in the LargeIcon
    // TODO: Set CATEGORY_EVENT
    // TODO: We can add actions, but we can't add icons or make them be ACTION_VIEW mapUrl actions or have icons...
    // - Look up SharedPreference for whether we want to play sounds?
    const eventTime = event.start_time; // TODO: need to get only as string
    const eventLocation = event.venue.name;
    const notificationTitle = event.name;
    const notificationMessage = `${eventTime}: ${eventLocation}`;
    const notificationExpandedText = event.description;
    const canVibrate = await PermissionsAndroid.checkPermission('android.permission.VIBRATE');
    PushNotification.localNotification({
        /* Android Only Properties */
        id: hashCode('upcoming:' + event.id).toString(), // (optional) Valid unique 32 bit integer specified as string. default: Autogenerated Unique ID
        // ticker: "My Notification Ticker", // (optional) used for accessibility
        autoCancel: true, // (optional) default: true
        //TODO:largeIcon: 'eventFlyerimageBitmap',
        smallIcon: 'ic_penguin_head_outline', // (optional) default: "ic_notification" with fallback for "ic_launcher"
        bigText: notificationExpandedText, // (optional) default: "message" prop
        subText: 'Open Event', // (optional) default: none
        color: purpleColors[2], // (optional) default: system default
        vibrate: canVibrate, // (optional) default: true
        vibration: 300, // vibration length in milliseconds, ignored if vibrate=false, default: 1000
        tag: 'upcoming_email', // (optional) add tag to message
        group: 'upcoming_email', // (optional) add message to group on watch
        ongoing: false, // (optional) set whether this is an "ongoing" notification

        /* iOS only properties */
        //alertAction: // (optional) default: view
        //category: // (optional) default: null
        //userInfo: // (optional) default: null (object containing additional notification data)

        /* iOS and Android properties */
        title: notificationTitle, // (optional, for iOS this is only used in apple watch, the title will be the app name on other iOS devices)
        message: notificationMessage, // (required)
        playSound: true, // (optional) default: true
        soundName: 'happening', // (optional) Sound to play when the notification is shown. Value of 'default' plays the default sound. It can be set to a custom sound such as 'android.resource://com.xyz/raw/my_sound'. It will look for the 'my_sound' audio file in 'res/raw' directory and play it. default: 'default' (default sound is played)
        //number: '10', // (optional) Valid 32 bit integer specified as string. default: none (Cannot be zero)

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
    console.log( 'NOTIFICATION:', notification );
    const notificationsEnabled = true;
    const notificationsUpcomingEventsEnabled = true;
    if (notification.userInteraction) {
      console.log('aaa', navigatePop, selectTab);
      if (notification.openedEventId) {
        console.log('OPENED ', notification.openedEventId);
        const notificationEvent = await fetchEvent(notification.openedEventId);
        const dispatch = this.dispatch;
        const navName = 'EVENT_NAV';
        const destState = {key: 'EventView', title: notificationEvent.name, event: notificationEvent};
        //TODO: factor out some of this navigation functionality
        await dispatch(selectTab('events'));
        await dispatch(navigatePop(navName));
        await dispatch(navigatePop(navName));
        await dispatch(navigatePush(navName, destState));
      }
    } else {
      if (notification.notification_type === 'EVENT_REMINDER') {
        if (notificationsEnabled && notificationsUpcomingEventsEnabled) {
          const notificationEvent = await fetchEvent(notification.event_id);
          this.sendUpcomingEventReminder(notificationEvent);
        }
      }
    }
  }
}

export function setup(store: Object) {
  const handler = new Handler(store);

  PushNotification.configure({
      // (optional) Called when Token is generated (iOS and Android)
      onRegister: async function (tokenRegistration: TokenRegistration) {
        setupMixpanelToken(tokenRegistration);
        await saveToken(tokenRegistration);
      },

      // (required) Called when a remote or local notification is opened or received
      onNotification: handler.receivedNotification,

      // ANDROID ONLY: GCM Sender ID (optional - not required for local notifications, but is need to receive remote push notifications)
      senderID: '911140565156',

      // IOS ONLY (optional): default: all - Permissions to register.
      permissions: {
          alert: true,
          badge: true,
          sound: true
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
