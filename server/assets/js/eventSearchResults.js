/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import url from 'url';
import FormatText from 'react-format-text';
import moment from 'moment';
import upperFirst from 'lodash/upperFirst';
import {
  injectIntl,
  intlShape,
} from 'react-intl';
import LazyLoad from 'react-lazyload';
import { StickyContainer, Sticky } from 'react-sticky';
import Masonry from 'react-masonry-component';
import Slider from 'react-slick';
import Collapse, { Panel } from 'rc-collapse';
import {
  intlWeb,
} from 'dancedeets-common/js/intl';
import type {
  Cover,
  JSONObject,
} from 'dancedeets-common/js/events/models';
import {
  BaseEvent,
  Event,
  SearchEvent,
} from 'dancedeets-common/js/events/models';
import type {
  NewSearchResponse,
  Onebox,
} from 'dancedeets-common/js/events/search';
import {
  formatStartEnd,
  weekdayDate,
  weekdayTime,
} from 'dancedeets-common/js/dates';
import {
  formatAttending,
} from 'dancedeets-common/js/events/helpers';
import {
  Card,
  ImagePrefix,
  wantsWindowSizes,
} from './ui';
import type {
  windowProps,
} from './ui';

require('slick-carousel/slick/slick.css');
require('slick-carousel/slick/slick-theme.css');
require('../css/slick.scss');
require('../css/rc-collapse.scss');

/*
import {
  yellowColors,
} from '../ui/Colors';
*/
// TODO: Copies from mobile/js/ui/Colors.js
const yellowColors = [
  '#FFF3B0',
  '#FFEA73',
  '#FFD802',
  '#FFCA01',
  '#C0A000',
];

export class SquareEventFlyer extends React.Component {
  props: {
    event: SearchEvent;
    lazyLoad?: boolean;
  }

  generateCroppedCover(picture: Cover, width: number, height: number) {
    const parsedSource = url.parse(picture.source, true);
    parsedSource.query = { ...parsedSource.query, width, height };
    const newSourceUrl = url.format(parsedSource);

    return {
      source: newSourceUrl,
      width,
      height,
    };
  }

  render() {
    const event = this.props.event;
    const picture = event.picture;
    if (!picture) {
      return null;
    }
    const width = 180;
    const height = 180;

    const scaledHeight = '100'; // height == width

    const croppedPicture = this.generateCroppedCover(picture, width, height);
    let imageTag = (<div
      style={{
        height: 0,
        paddingBottom: `${scaledHeight}%`,
      }}
    >
      <img
        role="presentation"
        src={croppedPicture.source}
        style={{
          width: '100%',
        }}
        className="no-border"
      />
    </div>
    );
    if (this.props.lazyLoad) {
      imageTag = <LazyLoad height={height} once offset={300}>{imageTag}</LazyLoad>;
    }
    return (
      <a className="link-event-flyer" href={event.getUrl()}>
        {imageTag}
      </a>
    );
  }
}

export class HorizontalEventFlyer extends React.Component {
  props: {
    event: SearchEvent;
  }

  generateCroppedCover(picture: Cover, width: number, height: number) {
    const parsedSource = url.parse(picture.source, true);
    parsedSource.query = { ...parsedSource.query, width, height };
    const newSourceUrl = url.format(parsedSource);

    return {
      source: newSourceUrl,
      width,
      height,
    };
  }

  render() {
    const event = this.props.event;
    const picture = event.picture;
    if (!picture) {
      return null;
    }
    const width = 800;
    const height = 400;

    const scaledHeight = '50'; // height == width * 50%

    const croppedPicture = this.generateCroppedCover(picture, width, height);
    const imageTag = (<div
      style={{
        height: 0,
        paddingBottom: `${scaledHeight}%`,
      }}
    >
      <img
        role="presentation"
        src={croppedPicture.source}
        style={{
          width: '100%',
        }}
        className="no-border"
      />
    </div>
    );
    return (
      <a className="link-event-flyer" href={event.getUrl()}>
        {imageTag}
      </a>
    );
  }
}

class _EventDescription extends React.Component {
  props: {
    event: SearchEvent;
    indexingBot: boolean;

    // Self-managed props
    intl: intlShape;
  }

  render() {
    const event = this.props.event;
    const keywords = [...event.annotations.categories];
    if (this.props.indexingBot) {
      keywords.push(...event.annotations.keywords);
    }

    let rsvpElement = null;
    if (event.rsvp && (event.rsvp.attending_count || event.rsvp.maybe_count)) {
      rsvpElement = (
        <ImagePrefix iconName="users">
          {formatAttending(this.props.intl, event.rsvp)}
        </ImagePrefix>
      );
    }

    return (
      <div>
        <h3 className="event-title">
          <a href={event.getUrl()}>
            <span>{event.name}</span>
          </a>
        </h3>
        <ImagePrefix
          icon={require('../img/categories.png')} // eslint-disable-line global-require
        >
          {keywords.join(', ')}
        </ImagePrefix>
        <ImagePrefix iconName="clock-o">
          {formatStartEnd(event.start_time, event.end_time, this.props.intl)}
        </ImagePrefix>
        <ImagePrefix iconName="map-marker">
          <div>{event.venue.name}</div>
          <FormatText>{event.venue.streetCityStateCountry('\n')}</FormatText>
        </ImagePrefix>
        {rsvpElement}
      </div>
    );
  }
}
const EventDescription = injectIntl(_EventDescription);

class HorizontalEvent extends React.Component {
  props: {
    event: BaseEvent;
    lazyLoad: boolean;
  }

  render() {
    const event = this.props.event;
    return (
      <Card className="wide-event clearfix">
        <div className="event-image">
          <SquareEventFlyer event={this.props.event} lazyLoad={this.props.lazyLoad} />
        </div>
        <div className="event-description">
          <EventDescription event={this.props.event} />
        </div>
      </Card>
    );
  }
}

class VerticalEvent extends React.Component {
  props: {
    event: BaseEvent;
  }

  render() {
    const event = this.props.event;
    return (<Card
      style={{
        display: 'inline-block',
        width: 200,
        verticalAlign: 'top',
      }}
    >
      <SquareEventFlyer event={event} />
      <h3 className="event-title" style={{ marginTop: 10 }}>
        <a href={event.getUrl()}>
          <span>{event.name}</span>
        </a>
      </h3>
      <div className="event-city">
        <div>{event.venue.name}</div>
        <FormatText>{event.venue.streetCityStateCountry('\n')}</FormatText>
      </div>
    </Card>);
  }
}

class FeaturedEvent extends React.Component {
  props: {
    event: BaseEvent;
  }

  render() {
    const event = this.props.event;
    return (
      <Card>
        <HorizontalEventFlyer event={event} />
        <h3 className="event-title" style={{ marginTop: 10 }}>
          <a href={event.getUrl()}>
            <span>{event.name}</span>
          </a>
        </h3>
      </Card>
    );
  }
}
class FeaturedEvents extends React.Component {
  props: {
    events: Array<BaseEvent>;
  }

  render() {
    if (!this.props.events.length) {
      return null;
    }

    const resultItems = [];
    const imageEvents = this.props.events.filter(x => x.picture);
    imageEvents.forEach((event, index) => {
      // Slider requires children to be actual HTML elements.
      resultItems.push(<div key={event.id}>
        <FeaturedEvent event={event} />
      </div>);
    });

    const results = resultItems.length > 1
      ? <Slider autoplay dots>{resultItems}</Slider>
      : resultItems;

    return (<div>
      <div>Featured Events:</div>
      <div style={{ width: '100%', padding: 10 }}>
        {results}
      </div>
    </div>);
  }
}

class CurrentEvents extends React.Component {
  props: {
    events: Array<SearchEvent>;
  }

  render() {
    if (!this.props.events.length) {
      return null;
    }

    const resultItems = [];
    this.props.events.forEach((event, index) => {
      resultItems.push(<VerticalEvent key={event.id} event={event} />);
    });

    return (<div>
      <div>Events Happening Now:</div>
      <div style={{ width: '100%', padding: 10 }}>
        <Masonry>
          {resultItems}
        </Masonry>
      </div>
    </div>);
  }
}

class _EventsList extends React.Component {
  props: {
    events: Array<SearchEvent>;

    // Self-managed props
    intl: intlShape;
  }

  render() {
    const resultItems = [];
    let currentDate = null;
    let currentTime = null;
    this.props.events.forEach((event, index) => {
      const eventStart = moment(event.start_time);
      const eventStartDate = upperFirst(this.props.intl.formatDate(eventStart.toDate(), weekdayDate));
      const eventStartTime = upperFirst(this.props.intl.formatDate(eventStart.toDate(), weekdayTime));
      if (eventStartDate !== currentDate) {
        resultItems.push(<li key={eventStartDate} className="wide-event day-header"><Sticky className="opaque">{eventStartDate}</Sticky></li>);
        currentDate = eventStartDate;
        currentTime = null;
      }
      if (eventStartTime !== currentTime) {
        resultItems.push(<li key={`${eventStartDate} ${eventStartTime}`}><b>{eventStartTime}</b></li>);
        currentTime = eventStartTime;
      }
      resultItems.push(<li key={event.id}><HorizontalEvent key={event.id} event={event} lazyLoad={index > 8} /></li>);
    });

    return (
      <StickyContainer>
        <ol className="events-list">
          {resultItems}
        </ol>
      </StickyContainer>
    );
  }
}
const EventsList = injectIntl(_EventsList);

class _OneboxLinks extends React.Component {
  props: {
    links: Array<Onebox>;
  }

  render() {
    if (!this.props.links.length) {
      return null;
    }
    const oneboxList = this.props.links.map(onebox =>
      <li key={onebox.url}><a className="link-onebox" href={onebox.url}>{onebox.title}</a></li>
    );

    return (
      <div>
        <ul>{oneboxList}</ul>
      </div>
    );
  }
}
const OneboxLinks = injectIntl(_OneboxLinks);

type PersonData = {
  id: String,
  name: String,
  count: Number,
};

class PersonList extends React.Component {
  props: {
    title: String;
    subtitle: String;
    categoryOrder: Array<String>;
    people: {[category: String]: Array<PersonData>};
  }

  state: {
    category: string;
  }

  constructor(props) {
    super(props);
    this.state = {
      category: '',
    };
  }

  render() {
    const peopleList = this.props.people[this.state.category].slice(0, 10);
    const categories = this.props.categoryOrder.filter(x => x === '' || this.props.people[x]);

    const selector = (<form className="form-inline" style={{ padding: 5 }}>
      <b>{this.props.title} by Style: </b>
      <select
        className="form-control form-inline"
        onChange={e => this.setState({ category: e.target.value })}
      >
        {categories.map(x => <option key={x} value={x}>{x || 'Overall'}</option>)}
      </select>
    </form>);
    return (<div>
      {selector}
      <i>{this.props.subtitle}:</i><br />
      <ul>
        {peopleList.map(x => <li key={x.id}><a href={`https://www.facebook.com/${x.id}`}>{x.name}</a></li>)}
      </ul>
    </div>);
  }
}

function AdminList(props) {
  return (<PersonList
    title="Promoters"
    subtitle="If you want organize an event, work with these folks"
    {...props}
  />);
}

function AttendeeList(props) {
  return (<PersonList
    title="Influencers"
    subtitle="If you want to connect with the dance scene, hit these folks up"
    {...props}
  />);
}

class _ResultsList extends React.Component {
  props: {
    response: NewSearchResponse;
    past: boolean;
    categoryOrder: Array<String>;

    // Self-managed props
    window: windowProps;
  }

  getPeoplePanel() {
    let peoplePanel = null;
    const admins = this.props.response.people.ADMIN;
    const attendees = this.props.response.people.ATTENDEE;
    if (admins || attendees) {
      const adminsList = (<AdminList
        people={admins}
        categoryOrder={this.props.categoryOrder}
      />);
      const attendeesList = (<AttendeeList
        people={attendees}
        categoryOrder={this.props.categoryOrder}
      />);

      if (this.props.window && this.props.window.width < 768) {
        peoplePanel = [
          <Panel key="people1" header="Nearby Promoters">{adminsList}</Panel>,
          <Panel key="people2" header="Nearby Influencers">{attendeesList}</Panel>,
        ];
      } else {
        peoplePanel = (
          <Panel key="people" header="Nearby Promoters & Influencers">
            <div className="row">
              <div className="col-sm-6">
                {adminsList}
              </div>
              <div className="col-sm-6">
                {attendeesList}
              </div>
            </div>
          </Panel>
        );
      }
    }
    return peoplePanel;
  }

  render() {
    const resultEvents = this.props.response.results.map(eventData => new SearchEvent(eventData));
    console.log('featuredInfos:', this.props.response.featuredInfos);
    const featuredInfos = (this.props.response.featuredInfos || []).map(x => ({ ...x, event: new Event(x.event) }));

    const now = moment();
    let eventsList = null;
    let eventCount = null;
    if (this.props.past) {
      const pastEvents = resultEvents.filter(event => moment(event.start_time) < now);
      eventsList = <EventsList events={pastEvents} />;
      eventCount = pastEvents.length;
    } else {
      // DEBUG CODE:
      // const currentEvents = resultEvents.filter(event => moment(event.start_time) > now);
      const currentEvents = resultEvents.filter(event => moment(event.start_time) < now && moment(event.end_time) > now);
      const futureEvents = resultEvents.filter(event => moment(event.start_time) > now);
      eventsList = [
        <CurrentEvents key="current" events={currentEvents} />,
        <EventsList key="future" events={futureEvents} />,
      ];
      eventCount = currentEvents.length + futureEvents.length;
    }
    console.log(eventCount);

    let featuredPanel = null;
    if (featuredInfos.length) {
      featuredPanel = (
        <Panel key="featured" header="Featured Event">
          <FeaturedEvents events={featuredInfos.map(x => x.event)} />
        </Panel>
      );
    }
    const peoplePanel = this.getPeoplePanel();

    let oneboxPanel = null;
    if (this.props.response.onebox_links.length) {
      oneboxPanel = (
        <Panel key="onebox" header="Related Links">
          <OneboxLinks links={this.props.response.onebox_links} />
        </Panel>
      );
    }
    const defaultKeys = ['featured', 'onebox', 'events'];
    if (eventCount < 5) {
      defaultKeys.push('people', 'people1', 'people2');
    }

    return (<Collapse defaultActiveKey={defaultKeys}>
      {featuredPanel}
      {peoplePanel}
      {oneboxPanel}
      <Panel key="events" header="Upcoming Events">
        {eventsList}
      </Panel>
    </Collapse>);
  }
}
const ResultsList = wantsWindowSizes(_ResultsList);

export default intlWeb(ResultsList);
