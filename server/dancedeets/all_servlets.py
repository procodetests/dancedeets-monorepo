# We import these for their side-effects in adding routes to the wsgi app
import dancedeets.battle_brackets.signup_servlets
import dancedeets.brackets.servlets
import dancedeets.classes.class_pipeline
import dancedeets.classes.class_servlets
import dancedeets.event_attendees.popular_people
import dancedeets.event_scraper.keyword_search
import dancedeets.event_scraper.source_servlets
import dancedeets.event_scraper.scraping_tasks
import dancedeets.event_scraper.thing_scraper2
import dancedeets.event_scraper.webhooks
import dancedeets.events.event_reloading_tasks
import dancedeets.events.find_access_tokens
import dancedeets.favorites.servlets
import dancedeets.logic.unique_attendees
import dancedeets.mail.webhooks
import dancedeets.ml.gprediction_servlets
import dancedeets.notifications.added_events
import dancedeets.notifications.rsvped_events
import dancedeets.pubsub.pubsub_tasks
import dancedeets.pubsub.facebook.auth_setup
import dancedeets.pubsub.twitter.auth_setup
import dancedeets.pubsub.weekly_images
import dancedeets.rankings.rankings_servlets
import dancedeets.scrape_apis.jwjam
import dancedeets.search.search_servlets
import dancedeets.search.search_tasks
import dancedeets.search.style_servlets
import dancedeets.search.search_source
import dancedeets.servlets.admin
import dancedeets.servlets.api
import dancedeets.servlets.calendar
import dancedeets.servlets.event
import dancedeets.servlets.event_proxy
import dancedeets.servlets.feedback
import dancedeets.servlets.login
import dancedeets.servlets.mobile_apps
import dancedeets.servlets.private_apis
import dancedeets.servlets.promote
import dancedeets.servlets.profile_page
import dancedeets.servlets.static
import dancedeets.servlets.static_db
import dancedeets.servlets.test_servlets
import dancedeets.servlets.tools
import dancedeets.servlets.youtube_simple_api
import dancedeets.sitemaps.events
import dancedeets.sitemaps.serve
import dancedeets.topics.topic_servlets
import dancedeets.tutorials.servlets
import dancedeets.users.user_event_tasks
import dancedeets.users.user_servlets
import dancedeets.users.user_tasks
import dancedeets.util.batched_mapperworker
import dancedeets.util.ah_handlers
import dancedeets.web_events.fb_events_servlets
import dancedeets.web_events.web_events_servlets
