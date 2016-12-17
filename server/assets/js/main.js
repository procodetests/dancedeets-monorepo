/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

require('trackjs');
require('jquery.backstretch');
require('jquery.smartbanner');
require('bootstrap');
require('./all-css');
import jQuery from 'jquery';
import './stackdriver-errors';
import fbSetup from './fb';
import fixStickyTouch from './sticky-touch';
import appInstallPromos from './app-install-promo';

global.$ = global.jQuery = jQuery;

fbSetup(window.fbPermissions, window.fbAppId, window.baseHostname);

if (window.showSmartBanner) {
  jQuery.smartbanner({
    title: 'DanceDeets',
    author: 'DanceDeets',
    icon: '/images/ic_launcher_dancedeets.png',
  });
}

jQuery(document).ready(() => {
  jQuery(document).on('click', '.mega-menu .dropdown-menu', (e) => {
    e.stopPropagation();
  });

  fixStickyTouch();
  appInstallPromos();

  // background-image rotation
  let images = [
    'dist/img/background-show-locking.jpg', // slim
    'dist/img/background-class-overhead.jpg', // cricket
    'dist/img/background-club-turntable.jpg', // mario
    'dist/img/background-show-awards.jpg', // slim

    'dist/img/background-class-kids.jpg', // mario
    'dist/img/background-show-pose.jpg', // slim
    'dist/img/background-club-smoke-cypher.jpg', // mario
    'dist/img/background-class-rocking.jpg', // mario
    'dist/img/background-show-dj.jpg', // slim
//    'dist/img/background-club-headspin.jpg',
  ];
  if (jQuery(document).width() > 900) {
    images = images.map(x => x.replace('.jpg', '@2x.jpg'));
  }
  jQuery('.fullscreen-static-image').backstretch(images, { duration: 8000, fade: 1500 });

  // animate-on-hover
  jQuery('.animate-on-hover').hover(() => {
    const action = jQuery(this).data('action');
    jQuery(this).addClass(`animated ${action}`);
  });
  jQuery('.animate-on-hover').bind('animationend webkitAnimationEnd oAnimationEnd MSAnimationEnd', () => {
    const action = jQuery(this).data('action');
    jQuery(this).removeClass(`animated ${action}`);
  });

  jQuery('#location_submit').click(() => Boolean(jQuery('#location').val()));
});
