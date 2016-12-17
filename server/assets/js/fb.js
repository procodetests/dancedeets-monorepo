import EventEmitter from 'eventemitter3';
import jQuery from 'jquery';

require('jquery.cookie');

export const fbLoadEmitter = new EventEmitter();

const FBSetup = (fbPermissions, fbAppId, baseHostname) => {
  let loginPressed = false;

  function deleteLoginCookies() {
    const cookieOptions = {
      domain: `.${baseHostname}`,
      path: '/',
    };
    jQuery.removeCookie(`fbsr_${fbAppId}`, cookieOptions);
    jQuery.removeCookie(`user_login_${fbAppId}`, cookieOptions);
  }

  function reloadWithNewToken() {
    if (String(window.location).indexOf('?') === -1) {
      window.location += '?nt=1';
    } else {
      window.location += '&nt=1';
    }
  }

  function currentUser() {
    const userLogin = jQuery.cookie(`user_login_${fbAppId}`);
    if (userLogin) {
      return JSON.parse(userLogin).uid;
    }
    return null;
  }

  function handleStatusChange(response) {
    if (response.status === 'connected') {
      if (response.authResponse.userID !== currentUser()) {
        if (loginPressed) {
          // Only do this for explicit logins, not for auto-logins
          window.mixpanel.track('Login - Completed');
        }
        // reload through endpoint to set up new user cookie serverside
        // TODO(lambert): Add a full-screen overlay explaining what we are doing...
        reloadWithNewToken();
      }
    } else if (response.status === 'not_authorized') {
      // Disabled as long as we have the App Tokens creating logged-in users without a proper FB token
      // if (currentUser()) {
      //   // the user is logged in to Facebook, but not connected to the app
      //   deleteLoginCookies();
      //   // TODO(lambert): Add a full-screen overlay explaining what we are doing...
      //   reloadWithNewToken('not_authorized');
      // }
    } else {
      // the user isn't even logged in to Facebook.

      // This can happen if the user changes their password, and Facebook auto-deletes the Facebook cookie.
      // So delete the user_login_ cookies here, so that we correctly detect a login (when they've re-logged in)
      deleteLoginCookies();
    }
  }

  function initFBCode(FB) {
    function login() {
      loginPressed = true;
      window.mixpanel.track('Login - FBLogin Button Pressed');
      FB.login((/* response */) => {}, {
        scope: fbPermissions,
      });
    }

    function logout() {
      window.mixpanel.track('Logout');
      // Seems the logout callback isn't being called, so ensure we delete the cookie here
      deleteLoginCookies();
      FB.getLoginStatus((response) => {
        if (response.status === 'connected') {
          FB.logout((/* response */) => {
            window.location.reload();
          });
        } else {
          window.location.reload();
        }
      });
    }

    FB.init({ version: 'v2.8', appId: fbAppId, status: true, cookie: true, xfbml: true });
    window.hasCalledFbInit = true;
    fbLoadEmitter.emit('fb-load');
    FB.Event.subscribe('auth.statusChange', handleStatusChange);
    FB.getLoginStatus((response) => {
      handleStatusChange(response);
    });

    jQuery('.onclick-login').on('click', login);
    jQuery('.onclick-logout').on('click', logout);
  }

  window.fbAsyncInit = () => {
    initFBCode(window.FB);
  };

  /**
   * It'd be nice to stick this in the html page directly, for faster FB loading.
   * But we need this code to run *after* we set window.fbAsyncInit above.
   * TODO: If we want to speed this up, we need to ensure the race conditions
   * can work if FB code loads before this fb.js code (as part of the merged bundle).
   */

  // Facebook/Login Code
  ((d, s, id) => {
    const fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {
      return;
    }
    const js = d.createElement(s);
    js.id = id;
    js.src = 'https://connect.facebook.net/en_US/sdk.js';
    fjs.parentNode.insertBefore(js, fjs);
  })(document, 'script', 'facebook-jssdk');
};

module.exports = FBSetup;

