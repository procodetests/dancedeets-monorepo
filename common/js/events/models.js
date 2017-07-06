/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import url from 'url';

type JSON = string | number | boolean | null | JSONObject | JSONArray;
export type JSONObject = { [key: string]: JSON };
type JSONArray = Array<JSON>;
type MiniImageProp = {
  uri: string,
  width: number,
  height: number,
};

const squareImageSize = 180;

export type Cover = {
  source: string,
  height: number,
  width: number,
};

export class JsonDerivedObject {
  constructor(data: any) {
    Object.keys(data).forEach(attr => {
      (this: any)[attr] = data[attr];
    });
  }
}

export class Venue extends JsonDerivedObject {
  geocode: ?{
    latitude: number,
    longitude: number,
  };
  address: ?{
    street: string,
    city: string,
    state: string,
    zip: string,
    country: string,
  };
  name: ?string;
  id: ?string;

  fullAddress(seperator: string = ', ') {
    if (this.address) {
      return [this.name, this.address.street, this.cityStateCountry()]
        .filter(x => x)
        .join(seperator);
    } else {
      return this.name;
    }
  }

  streetCityStateCountry(seperator: string = ', ') {
    if (this.address) {
      return [this.address.street, this.cityStateCountry()]
        .filter(x => x)
        .join(seperator);
    } else {
      return null;
    }
  }

  cityState(seperator: string = ', ') {
    if (this.address) {
      return [this.address.city, this.address.state]
        .filter(x => x)
        .join(seperator);
    } else {
      return null;
    }
  }

  cityStateCountry(separator: string = ', ') {
    if (this.address) {
      return [this.address.city, this.address.state, this.address.country]
        .filter(x => x)
        .join(separator);
    } else {
      return null;
    }
  }
}

export type Admin = {
  id: string,
  name: string,
};

export type EventRsvpList = {
  attending_count: number,
  maybe_count: number,
};

export class BaseEvent extends JsonDerivedObject {
  id: string;
  name: string;
  start_time: string; // eslint-disable-line camelcase
  end_time: ?string; // eslint-disable-line camelcase
  picture: ?Cover;
  venue: Venue;

  constructor(eventData: JSONObject) {
    super(eventData);
    this.venue = new Venue(eventData.venue);
  }

  getUrl() {
    return `https://www.dancedeets.com/events/${this.id}/`;
  }

  startTimeNoTz() {
    return this.start_time.substr(0, 19);
  }
  endTimeNoTz() {
    return this.end_time ? this.end_time.substr(0, 19) : null;
  }
}

export class SearchEvent extends BaseEvent {
  rsvp: ?EventRsvpList;
  annotations: {
    categories: Array<string>,
    keywords: Array<string>,
  };
}

export class Event extends BaseEvent {
  description: string;
  source: {
    url: string,
    name: string,
  };
  rsvp: ?EventRsvpList;
  picture: ?Cover;
  venue: Venue;
  annotations: {
    categories: Array<string>,
    creation: {
      creator: ?string,
      creatorName: ?string,
      method: string,
      time: string,
    },
  };
  language: string;
  admins: Array<Admin>;
  ticket_uri: string; // eslint-disable-line camelcase

  getFlyer(dimensions: { width?: number, height?: number }): ?MiniImageProp {
    if (!this.picture) {
      return null;
    }

    let { width, height } = dimensions;
    if (!width && !height) {
      return {
        uri: this.picture.source,
        width: this.picture.width,
        height: this.picture.height,
      };
    }

    const ratio = this.picture.width / this.picture.height;
    if (!height && width) {
      height = Math.floor(width / ratio);
    } else if (!width && height) {
      width = Math.floor(height / ratio);
    }
    const parsedSource = url.parse(this.picture.source, true);
    // Careful! We are re-using parsedSource here.
    // If we do more complex things, we may need to create and modify copies...
    parsedSource.query = { ...parsedSource.query, width, height };
    const result = {
      uri: url.format(parsedSource),
      width,
      height,
    };
    return result;
  }

  getSquareFlyer(): ?MiniImageProp {
    return this.getFlyer({ width: squareImageSize, height: squareImageSize });
  }

  getResponsiveFlyers(): Array<MiniImageProp> {
    if (!this.picture) {
      return [];
    }
    return [320, 480, 720, 1080, 1440].map(width => this.getFlyer({ width }));
  }
}
