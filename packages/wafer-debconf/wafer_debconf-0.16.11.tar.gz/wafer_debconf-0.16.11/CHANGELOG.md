# Changelog

# 0.16.11
- Minor improvements towards DebConf25:
  - Ensure arrival dates are before departure dates.
  - A mechanism to close daytrips.
  - Clearer waitlists for day-trips.
  - Allow for a heirarchy of rooms, separated by colon, to make it
    easier to declare "building-mates".
  - Show roommate arrival and departure times.
  - Replace Key Card with Transit Card in CheckIn.

# 0.16.10

- Minor improvements towards DebConf25:
 - Include RECONFIRMATION in the `context_processor`
 - Show registration status on profile page.
 - Clarify that need applies to travel bursaries.
 - Don't invoice for the daytrip while only waitlisted for it
 - Mechanism to close accommodation registration.
 - Stripe payment JS upgrade.

# 0.16.9

- Minor improvements towards DebConf25:
  - Export for security information.
  - Show free attendees differently to fully paid attendees in the front desk.
  - Explain fitted cuts in t-shirt help text.
  - Allow registration team admins to delete queue slots.
  - Some bug fixes to the talks export.

# 0.16.8

- Bug fix for 0.16.7:
 - Show paid accommodation options after bursaries are denied.
- Visa Team permissions
- Tweaks to the bursary denial email
- Talks export, include: submission time, email addresses, gender demographics.

# 0.16.7

- Bug-fixes for 0.16.6:
  - A couple of 500s
  - Grant export visibility to the Registration Admin team.
  - Allow bursary value estimation to be restricted to one component.
  - Fix a race in setting `completed_register_steps`, by not caching it.

# 0.16.6

- Bug-fix to 0.16.5:
  - Render the Bursary Referee admin page.

# 0.16.5

- Minor improvements towards DebConf25:
  - Don't let users URL hack too far into registration.
  - Fix double dots in bursary instructions link.
  - Categories for our new invoice items.
  - Handle `payment_intent` cancellation.
  - Only restrict budget choice options when we specified a user, fixing
    bursary admin edits.
  - Break up export permissions requirements, allowing a local orga team
    access to read-only data.
  - In Bursary Referee, show which budget the bursary was requested
    from.
  - settings: don't make attendee list public by default.

# 0.16.4

- Minor improvements towards DebConf25:
  - Display a notice on the bursary update page if there's nothing to
    update.

# 0.16.3

- Minor improvements towards DebConf25:
  - Serve all meals on the departure day, by default.
  - Allow replacing breakfast and lunch with brunch.

# 0.16.2

- Minor improvements towards DebConf25:
  - Allow attendees to select a bursary budget line for their request.
  - Add orga budget lines (behind a permission).

# 0.16.1

- Minor improvements towards DebConf25:
  - Put the info box around the entire security info section.
  - Improve the birthdate picker.
  - Improve the partial contribution rendering on the review page.
  - Show partial contributions on the profile page.
  - Use the citizenship country selector on the visa page.
  - Put the government data sharing instruction behind `DEBCONF_COLLECT_AFFILIATION`.

# 0.16.0

- Preparation for DebConf25:
  - Add support for collecting security information
  - Add a new permission for talkmeister tasks
  - Configurable departure day
  - Configurable `DEBCONF_ORGA_EARLY_DAYS`
  - Configurable T-shirt swap date
  - Use a permission for orga early arrival
  - Put validation restrictions on arrival and departure dates
  - Customizable departure time
  - Add a notice encouraging self-payment
  - Allow attendees to offer partial contributions towards bursary costs
- Some flags to filter the invoices we badger
- stats: speakers by country: count speakers only once

# 0.15.15

- Fix volunteer page queries
- Allow closing daytrip and daytrip insurance signup.

# 0.15.14

- Front Desk can issue invoices, when necessary.
- Correctly categorize daytrip income for stripe.
- Don't include refunds in invoice summaries for stripe.

# 0.15.13

- Fix `issue_invoice_without_bursary`.
- `load_schedule_grid`: Don't replace venue days.
- Management command to issue KSP IDs
- Restore `badger_unnecessary_invoices`.
- Avoid cancelling attendees with paid invoices in
  `cancel_unable_travel_without_bursary`.
- Add `badger_incomplete_registrations`.
- Render lists as lists in exports.
- Only include complete registrations in exports.
- Include a summary of speaker registration in the talk export
- Export of speakers registration states.
- Track bedding issuance in checkins.
- Don't attempt to create invoice lines, if we aren't creating the
  invoice.
- Day Trip registration.

# 0.15.12

- Render register statistics in static generation with bakery.
- Don't break the statistics view if there's a null travel bursary.
- Avoid creating null travel bursaries in the attendee bursary form.
- Allow increasing bursaries in the attendee bursary form, before the
  bursary deadline (like the registration form).
- A management command for retrying timed-out mailing list
  subscriptions.
- Clearer bursary data in the accommodation export.
- An accommodation nights export that collates attendees by night &
  option.
- Clarify bursary status wording in the profile page.

# 0.15.11

- debconf registration: Implement a timeout for mailing list
  subscriptions.

# 0.15.10

- templates: replace data-target with data-bs-target
- templates: venue: drop dots right after links
- templates: venue: turn HLS URL into an actual link

# 0.15.9

- minidebconf: admin: add accessor method for email
- minidebconf: admin: display email as readonly when editing as well

# 0.15.8

- Generalise the checkbox text for COVID-19 non-vaccinated attendees
- minidebconf: admin: list email instead of country twice

# 0.15.7

- debconf registration:
  - Fix typos
  - Fix registration forms, since the migration of bootstrap 5.
  - Migrate to tempus-dominus, with a separate date-range picker.
  - Add option to collect attendee affiliations.
  - Correctly set the accommodation option, even if there's only one and
    the widget isn't displayed.
  - Open links in new windows/tabs.
- Vendor tempus-dominus and popperjs.

# 0.15.6

- minidebconf: hack `pt_BR` translation for BH minidebconf

# 0.15.5

- minidebconf: registration: always display notes field

# 0.15.4

- minidebconf.forms: fix hiding notes when accomodation and travel are disabled
- minidebconf.admin: display `Registration.city_state`

# 0.15.3

- minidebconf.admin: display food/accomm/travel fields even if disabled

# 0.15.2

- minidebconf: add missing blank=True to fields with null=True

# 0.15.1

- stylesheet: fix sponsor logos CSS

# 0.15.0

- README.md: document minidc registration settings
- minidebconf: improve admin to manage registrations
- minidebconf: complete `pt_BR` translation
- minidebconf: admin: display user's full name when viewing registration

# 0.14.0

- setup.py: upgrade wafer to >= 0.16
- Add a vendored copy of bootstrap 5 JS and SCSS
- profile: move DebConf customizations to epilogue
- templates: replace data-toggle with data-bs-toggle
- templates: base: include default wafer stylesheet
- profile: drop JS bits that are already provided by wafer
- volunteers: drop reference do function removed in Django 4
- stylesheet: provide default style for navbar
- .gitlab-ci.yml: fix testing against different Django versions
- stylesheet: limit image width in the page text
- Add script to copy bootswatch themes
- Add all themes from bootswatch
- stylesheet: set navbar to primary color by default

# 0.13.2

- minidebconf: split extra registration fields in sections
- minidebconf: display extra info about shirt sizes and bursaries
- Complete `pt_BR` translation

# 0.13.1

- minidebconf: properly i18nize day names in the registration form

# 0.13.0

- Update portuguese translation and fix typos
- Update portuguese translation
- Update portuguese translation
- Add support for Django 4
- .gitlab-ci.yml: test against Django 4
- debconf.models: mark gender names for translation
- minidebconf.forms: don't ask for days when there are none
- templates: index.html: mark "View my profile" for translation
- scripts/i18n.sh: update translation files
- Update translation files
- debconf: add `pt_BR` translation
- .gitlab-ci.yml: test compiling translations
- minidebconf: allow translating names of initial set of pages
- minidebconf: add `pt_BR` translation of initial pages set
- minidebconf: add missing migration
- minidebconf: add simple accommodation and food request fields
- minidebconf: registration: allow setting a default country
- minidebconf: add travel reimbursement fields to registration
- minidebconf: only display bursary fields to Debian contributor and above
- minidebconf: set `verbose_name` for Registration.diet
- minidebconf: set `verbose_name` on `Registration.shirt_size`
- minidebconf: complete `pt_BR` translation

# 0.12.0

- We aren't py2 compatible
- A mechanism to attribute sponsorship from stripe
- Subclass the Meta when we subclass abstract models
- volunteers: fix off-by-one in date selector
- Slots don't necessarily have a defined `start_time`
- Management command to update etherpad URLs when they are archived
- Handle partial refunds
- Specify an encoding for CSV exports
- .gitlab-ci.yml: test against bookworm
- setup.py: lock on wafer < 0.15
- .gitlab-ci.yml: install more packages from Debian proper
- menu: don't link to `front_desk` unless enabled

# 0.11.10
- Fix some corner cases around reviewing free attendees.
- Hide GitHub and Twitter links
- Enable bootstrap popovers (used by the mugshots on profile pages)

# 0.11.9
- Don't delete `paid_separately` accommodation when passing the bursary
  page.
- Make creating accommodation objects in admin easier.

# 0.11.8
- Management command to issue an invoice.
- Sort attendance review form by registration order.
- Minor bug fixes

# 0.11.7
- Fix a couple of typos
- Don't attempt to invoice accommodation without a price, after the
  bursary deadline.

# 0.11.6

- Extend statistics to include statistics on free attendee reviews.
- Log bursary update requests.
- Include more information about bursary requests in the visa export.

# 0.11.5

- Add a review dashboard for `DEBCONF_REVIEW_FREE_ATTENDEES`.
- Some bug fixes for statistics pages.

# 0.11.4

- Add support for tracking externally-self-paid accommodation.
- Allow attendees to maintain their current accommodation option even if
  they wouldn't be able to select it, themselves.
- Allow accommodation options to include meals.

# 0.11.3

- Fix a crash in registration in 0.11.2.
- Reword instructions and some registration fields.
- Port badges to django-compressor.

# 0.11.2

- Allow Stripe payments to work for invoices when the <html> tag doesn't
  have an explicit lang.
- Track Registrations and Accommodation requests in Queues.
- Add `DEBCONF_REVIEW_FREE_ATTENDEES` to review free registration
  requests.

# 0.11.1

- Include static assets missed in 0.11

# 0.11

- Avoid crashes when exporting minidc sites
- A badger to remind people to collect their bursaries
- Add a --final argument to `badger_travel_reimbursement_reminder`
- Load moment from the main template
- Include dependent-visibility.js for registration form
- Use Debian's eonasdan-bootstrap-datetimepicker in the registration forms

# 0.10.2

- volunteers: drop deprecated python2 compatibility (this enables using this
  app together with Django 3)

# 0.10.1

- move `now` fixture to a shared location
- debconf.view: fix `get_current_slot()` to support start times from previous
  slots

## 0.10

* minidebconf: add phone number and registration type fields

## 0.9

* Upgrade to Django 3
* Replace `django.conf.urls.url` with `django.urls.re_path`
* Replace `ugettext_lazy` with `gettext_lazy`
* .gitlab-ci.yml: test against bullseye

## 0.8

* `test_registration`: use `register_form_factory` to get registration form
* minidebconf: registration: prevent registrations when they are closed
* Add Font Awesome 5
* stylesheet: use Font Awesome instead of Fork Awesome

## 0.7.1

* Minidebconf: Add optional diets and shirt sizes

## 0.7

* Import sponsor code from dc23
* stylesheet: import a "local" stylesheet

## 0.6.10

* Front Desk View: Track issuance of meal vouchers.

## 0.6.9

* `load_schedule_grid`: make creation of break items idempotent

## 0.6.8

* Add `DEBCONF_SKIPPED_MEALS` to avoid needing to serve breakfast on the
  first day.

## 0.6.7

* `load_schedule_grid`: create break items automatically

## 0.6.6

* `load_schedule_grid`: remove hack used for online DebConfs

## 0.6.5

* Fix queryset filtering bugs in badger_outstanding_invoices and
  cancel_unable_travel_without_bursary. Both were considering too many
  attendees.
* Don't issue 0-value invoices in re-invoicing.
* Allow attendees with early accommodation to go through the
  registration form without losing it.

## 0.6.4

* Fix some registration bugs in accommodation options.
* Fix a bug in the content statistics.
* Fix a bug in update_invoice_metadata.
* Fix a timestamp bug in load_schedule_grid.
* Create the video team in create_debconf_groups.
* Handle GUID EventIDs in load_videos.
* Improve the pricing wording around accommodation options.
* Add an export of visa requests.
* Extract and genericise badger_travel_bursaries from examples.
* Make badger_outstanding_invoices usable across events.
* Add a new terminal state for invoices - refunded.
* Add a management command to cancel registrations for attendees who
  didn't receive a travel bursary and selected the "unable" level of
  need.
* Add a management command to issue invoices to attendees who didn't
  receive bursaries.
* Add a management command to automatically reconfirm attendees, where
  possible.
* Add a pair of management commands to request reconfirmation.

## 0.6.3

* Hot-fix for 0.6.2, a bug in the accommodation options.

## 0.6.2

* Prompt bursary applicants to name the city they are travelling from
* badger_unregistered: If a user has multiple accounts, point this out to them
* Add a field to have accommodation options
* Store a breakdown of the invoice in Stripe Metadata

## 0.6.1

* Require agreement for regular testing, if unvaccinated.

## 0.6.0

* Python 3.10 support
* Make the currencies used for billing and bursaries configurable.
* Registration: Add COVID-19 vaccination page.
* Registration: Add a visa page.
* Registration: Fix some bugs in in-person debconfs, introduced in
  online debconf support.

## 0.5.3

* Extend the format for volunteer-tasks.yml

## 0.5.2

* add management command to send talk upload URLs

## 0.5.1

* display shipping addresses in bursary admin
* display "approx" next to the local currency on invoices

## 0.5.0

* schedule: allow filtering slots before a given time
* schedule: allow filtering slots by duration
* schedule: allow fuzzy matching of talk type and venue names
* schedule: make "spread" the default and only supported behavior

## 0.4.0

* load_schedule_grid: automate scheduling of breaks
* load_schedule_grid: load video flag if available
* add management command for automated scheduling
* Add infrastructure for minimal conference websites
  * debconf: move DCScheduleArrived view to register app
  * Provide infra for minimal conference apps
  * schedule: don't validate contiguousness of schedule items
  * minidebconf: add simple registration module
  * minidebconf: add i18n/l10n support
  * Add generic Salsa login
  * Extract home page features from dc20
  * Extract streaming/schedule features from dc20
  * Extract "wafer-debconf.scss" from dc20
  * `is_it_debconf`: fix crash when there is no ScheduleBlock
  * index: improve create/edit homepage controls
  * `context_processors`: always load site metadata
  * MANIFEST: include extra files
  * setup.py: add missing dependency
  * Make it easier to override theme
  * MANIFEST.in: publish .scss files from `debconf.themes.*`
  * .gitlab-ci.yml: run tests
  * debconf.context_processors: consolidate settings in a single function
  * minidebconf: add init_minidc_menu_pages management command
  * debconf.common_settings: get settings from the environment
  * debconf.common_settings: read salsa auth config from environment
  * debconf.context_processors: fix is_it_debconf
  * test_context_processors: fix tests wrt timezone
  * registration: require login
  * debconf.common_settings: provide default value for SANDBOX
  * settings: disable video reviewer for talk submissions
  * stylesheet: add minimal styling for the schedule table
  * schedule: drop "by" before speaker names
  * video player: vendor video.js and necessary plugins
  * Extract video player code from dc20
  * video player: fix mirror detection for current setup
  * video player: reload source on error
  * schedule: stop hiding time column for slots < 15 min
  * Extract now_or_next from dc20
  * Add some basic tests for create_online_service_urls
  * load_videos: concatenate baseurl instead of joining via os.path.join
  * load_videos: normalize leading and trailing slashes
  * load_videos: fix actual object creation/update
  * profile: hide "Submit talk" if submission is closed
  * profile: hide "not registered" warning if registration is closed
  * minidebconf: registration: support GET at /unregister/
  * .gitlab-ci.yml: also install python3-yaml
  * debconf.context_processors: improve readability
  * debconf.common_settings: take advantage of GeoIP redirector
  * debconf: profile: avoid crash when not using badges app
  * register.urls: fix import of DCScheduleArrived
  * .gitlab-ci.yml: add JS/CSS packages
  * setup.py: add new dependency: django_extensions
  * LICENSE: account for embedded copies files
  * setup: require wafer >= 0.11
  * ci: install dependencies witih pip
  * debconf.common_settings: drop deprecated `safe_mode` option for markitup

## 0.3.20

* invoice: display `DEBCONF_INVOICE_ADDRESS`

## 0.3.19

* Display shipping addresses in Attendee admin views
* Show totals for t-shirt and shoes in statistics

## 0.3.18

* Remove debconf.markdown, taken over by `mdx_staticfiles`
* remove dead code
* talk urls: use TalkUrl.public attribute from newer wafer

## 0.3.17

* talk: display language
* Remove wafer.schedule/venue.html override, not needed
* Describe the exports app

## 0.3.16

* Allow anonymous access to registration statistics.
* Build our public views into django-bakery static builds.
* Hide provisionally-accepted talks from public view, on user profiles.
* Fix rendering of talk edit pages, with django-markitup >= 3.7.
* Move the AoE explanation to `<abbr>`s
* Log shipping addresses during registration.

## 0.3.15

* Add `DEBCONF_INVOICE_ADDRESS` setting.
* Break up Shipping Address into separate fields.
* Make deadlines AoE.

## 0.3.14

* `badger_speakers_scheduled`: allow to mail speakers a second time
* `load_videos`: conform to the new sreview output format
* `load_videos`: overwrite videos

## 0.3.13

* Bug fixes to schedule timezone and volunteer permissions.

## 0.3.12

* Put auth on the volunteer views, so anonymous users get sent to log
  in, rather than 500ing.

## 0.3.11

* Volunteer tools:
  - Bug fixes for the volunteer timezone support.
  - Add a `required_permission` property to tasks.
  - Add a `task.accept_video_tasks` permission.

## 0.3.10

* Volunteer tools:
  - Allow importing video volunteer tasks from YAML, together with the
    ad-hoc tasks.
  - Display Volunteer views in the Volunteer's configured timezone.

## 0.3.9

* Tools for generating Jitsi, Etherpad, etc. URLs.

## 0.3.8

* schedule: improve navigation in single-day schedule pages.

## 0.3.7

* several improvements in the schedule:
  * drop track sidebar
  * improve display of local time
  * make video/no-video icon a bit smaller
  * add class to Time header cell to allow styling
  * add fullscreen mode

## 0.3.6

* generalize `badger_speakers_scheduled` to work for all future conferences.

## 0.3.5

* `load_schedule_grid`: schedule activities past midnight
* Add command to print a list of countries by talks, with notes

## 0.3.4

* Only look up the payment intent for new invoices
* bursary admin: list name and email

## 0.3.3

* Minor:
  * T-shirt instructions and help text.

## 0.3.2

* Minor:
  * Only mention expense bursaries, for online DebConfs, in confirmation
    emails, and the profile page.
  * Set registration completed timestamps.
  * Correctly determine registration completion in statistics, for
    online debconfs.
  * Render Kosovo, in country listings.
  * Include expense bursaries in admin views, statistics, exports.
  * Collect shipping addresses for online debconfs.

## 0.3.1

* Render invoices gracefully without Stripe credentials
* Add an event type breakdown to the content statistics

## 0.3.0

* Major changes:
  * Support DebConf Online (stripped down registration)
  * Replace PayPal payments with Stripe
* Bug fixes:
  * Avoid duplicating invoices when the total hasn't changed.

## 0.2.1

* Bug fixes:
  * Support anonymous views of the closed registration page
  * Drop unused imports
  * Drop use of six, we're py3k-only, baby
  * Fix volunteer statistics
  * Allow content statistics to render without a schedule
  * In Wafer > 0.7.7 slots have datetime fenceposts
  * Merge wafer.schedule templates from wafer 0.9.0
  * Django 2 compatibility: `is_authenticated` -> bool
  * Don't blow up if an event lost a venue
  * Fix volunteer admin
* Minor behavior changes:
  * Allow Content Admin to view users

## 0.2.0

* Port to Django 2:
  * Set `on_delete` on Foreign Keys
  * django.core.urlresolvers was renamed to django.urls in 1.10
  * Migration to update the bursaryreferee FK
* Port to wafer 0.9.0
  * debconf.views: fix against latest wafer >= 0.7.7
  * Update `load_schedule_grid` to support blocks
  * Make slot times TZ aware

## 0.1.22

* Move prices to a settings PRICES dict.

## 0.1.21

* Fix a bug in the bursary status, after DebConf has started.
* Add an invoice export.
* Add video player to talk pages.
* Simplify the volunteer task mapping data model.
* Mention the video team's advice for presenters, in the talk acceptance
  email.
* Add statistics pages for Volunteers and Content.
* Expose arrived and departed state to DCSchedule.
* Include Checked In state in bursary exports.
* Update the reimbursement email, to match current SPI requirements.

## 0.1.20

* UNKNOWN

## 0.1.19

* Support Conference Dinner in FD meal sales.
* Boldly show paid status in FD check-in.
* Set a deadline by which bursaries have to be approved, after which
  the user can be invoiced.
* Fail gracefully when a talk doesn't have a track (in the colouring
  code)
* Disable retroactive volunteering.

## 0.1.18

* More tweaks to video volunteer wrangling.

## 0.1.17

* Improve volunteer signup.
* Automate Video Team T-Shirt distribution.

## 0.1.16

* createtasks: load task template descriptions

## 0.1.15

* Add timestamps to Attendee's registration.
* Show if attendees registered late, in front desk.

## 0.1.14

* Allow volunteers to set their preferences.
* Return a 404 when a non-registered user tries to preview a badge.

## 0.1.13

* Support Postgres in the queue migration from 0.1.12

## 0.1.12

* Add a management command to create volunteer tasks from YAML
* Improve the track list in the schedule.
* Change registration permissions (only admins can take cash).
* Get badges working again.
* Assign keysigning IDs, and add a management command to sort them.

## 0.1.11

* Generalize the badger speaker script to all talk statuses.
* Add a keysigning export.

## 0.1.10

* Validate speaker attendance dates, when schedule editing.
* Use DebConf's custom schedule templates.
* Add Python 3.5 support to the load\_schedule\_grid command.

## 0.1.9

* Add a command to load schedule grid from YAML

## 0.1.8

* Add a badger for accepted talks
* Add travel\_from to the bursary export.

## 0.1.7

* List exports in front desk
* Add bursaries export

## 0.1.6

* Further improvements to the bursary notification email.

## 0.1.5

* Add management command to remind users to register.
* Include some details, useful for visas in the registration
  confirmation email.
* Handle unassigned rooms, correctly.
* Clear travel expense amount, when cancelling a travel bursary request.
* Add a CSV export for Child Care.
* Display meal lists, in order.
* Remove DC18 details from the bursary notification email.

## 0.1.4

* Correct the permission checked by bursary admin pages.

## 0.1.3

* Add a Volunteer Admin group.
* Add Kosovo to the list of countries.

## 0.1.2

* SECURITY: Don't show other registered attendees as room-mates, when
  nobody has rooms assigned.

## 0.1.1

* Package now has metadata and license.
* New management commands: `create_debconf_groups`,
  `load_tracks_and_talk_types`.

## 0.1.0

* Initial release, mostly ready for DebConf19.
