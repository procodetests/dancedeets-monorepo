/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import { intlWeb } from 'dancedeets-common/js/intl';
import { Event } from 'dancedeets-common/js/events/models';
import { addUrlArgs } from 'dancedeets-common/js/util/url';
import { NewEmailWrapper, buttonColor } from './mailCommon';

class GenericCircle extends React.Component {
  render() {
    return (
      <mj-image
        src="https://static.dancedeets.com/img/mail/purple-circle.png"
        width="50px"
        height="50px"
      />
    );
  }
}

class SellingPoint extends React.Component {
  props: {
    title: string,
    contents: string,
  };

  render() {
    return [
      <mj-table>
        <tr>
          <td>
            <GenericCircle />
          </td>
          <td style={{ fontWeight: 'bold' }}>{this.props.title}</td>
        </tr>
      </mj-table>,
      <mj-text>{this.props.contents}</mj-text>,
    ];
  }
}
class BodyWrapper extends React.Component {
  props: {
    event: Event,
    organizerEmail: string,
    organizerName: string,
  };

  render() {
    const event = this.props.event;
    const args = {
      utm_source: 'event_add',
      utm_medium: 'email',
      utm_campaign: 'event_add',
    };
    const url = event.getUrl(args);
    const shortUrl = `https://dd.events/e/${event.id}`;
    const address = event.venue.address;
    let city = 'your city';
    if (address && address.city) {
      city = `the ${address.city} area`;
    }
    // TODO: Handle 'intro email' different from 'second email'
    return [
      <mj-section class="alternate">
        <mj-column full-width="full-width" />
      </mj-section>,
      <mj-section>
        <mj-column full-width="full-width">
          <mj-text>
            <p>Hi there {this.props.organizerName},</p>
            <p>
              We want to help promote your new event and help grow our dance
              scene:
            </p>
            <p>“{event.name}”</p>
            <p>
              To start, we&#8217;ve added your event to DanceDeets, the
              world&#8217; s biggest street dance event platform:
            </p>
            <mj-button
              href={shortUrl}
              align="center"
              background-color={buttonColor}
            />

            <p>What does this mean for you?</p>
          </mj-text>

          <mj-table>
            <tr>
              <td>
                <GenericCircle />
              </td>
              <td>
                Your event is now accessible on dancedeets.com and our mobile{' '}
                app, for the 50,000+ dancers that visit us every month. Even if{' '}
                they don&#8217; t use Facebook.
              </td>
            </tr>
            <tr>
              <td>
                <GenericCircle />
              </td>
              <td>
                Easily discoverable by dancers living in {city} (or those just{' '}
                visiting!), as well as new dancers looking to get into the{' '}
                scene.
              </td>
              <td>
                <GenericCircle />
              </td>
              <td>
                We&#8217; ve published information about your event to Google{' '}
                and <a href="https://twitter.com/dancedeets">Twitter</a>, so{' '}
                dancers can find information about your event, no matter where{' '}
                they look.
              </td>
            </tr>
          </mj-table>

          <mj-text font-weight="bold">Want more promotion? Read on…</mj-text>
        </mj-column>
      </mj-section>,
      <mj-section>
        <mj-column>
          <SellingPoint
            title="THE most influencial dance event platform"
            contents="Over 250,000 events around the world, visited by over 50,000 dancers every month."
          />
        </mj-column>
        <mj-column>
          <SellingPoint
            title="Maximum exposure on multiple channels"
            contents="Website, mobile apps, Facebook, Instagram, Twitter… We will push your event to everywhere dancers look."
          />
        </mj-column>
      </mj-section>,
      <mj-section>
        <mj-column>
          <SellingPoint
            title="Ongoing event promotion support"
            contents="We will post/share footage and event recap after the event, to our 8,000 global followers on Facebook."
          />
        </mj-column>
        <mj-column>
          <SellingPoint
            title="Completely free!"
            contents="No fee! All you need to do is to help spread DanceDeets’ name to your local dancers.."
          />
        </mj-column>
      </mj-section>,
      <mj-button
        href="mailto:partnering@dancedeets.com"
        align="center"
        background-color={buttonColor}
      />,
    ];
  }
}

class AddEventEmail extends React.Component {
  props: {
    event: Event,
    organizerEmail: string,
    organizerName: string,

    mobileIosUrl: string,
    mobileAndroidUrl: string,
    emailPreferencesUrl: string,
  };

  render() {
    const event = new Event(this.props.event);
    return (
      <NewEmailWrapper
        previewText={`We want to help promote your event!`}
        mobileIosUrl={this.props.mobileIosUrl}
        mobileAndroidUrl={this.props.mobileAndroidUrl}
        emailPreferencesUrl={this.props.emailPreferencesUrl}
      >
        <BodyWrapper
          event={event}
          organizerEmail={this.props.organizerEmail}
          organizerName={this.props.organizerName}
        />
      </NewEmailWrapper>
    );
  }
}

export default intlWeb(AddEventEmail);
