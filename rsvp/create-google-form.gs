/**
 * Jack & Lucy — creates the RSVP Google Form and its response Sheet.
 *
 * Run once, signed in to the Google account that should own the replies.
 * Full steps are in rsvp/README.md. When it finishes, open
 * View → Logs (or the Execution log) and copy the block it prints into
 * index.html, over the existing `var RSVP_GOOGLE_FORM = { ... };`.
 */

// Name of an existing Drive folder to put the form and sheet in.
// Leave as is, or change it; if no folder of that name exists they stay in My Drive.
var DRIVE_FOLDER_NAME = 'Wedding';

// These must match index.html exactly — they're what the website sends.
var YES = "Yes - we can't wait to celebrate with you!";
var NO = 'No - sadly I am unable to join';

function createRsvpForm() {
  var form = FormApp.create('Jack & Lucy — RSVP');
  form.setDescription('Replies from the wedding website, 5th June 2027.');
  form.setCollectEmail(false);
  form.setAllowResponseEdits(false);
  form.setLimitOneResponsePerUser(false);   // no Google sign-in needed for guests
  form.setShowLinkToRespondAgain(false);

  // Same order as the website. Nothing is "required" here because the website
  // does the checking (and skips the later questions for people who can't come).
  var items = {
    name:        form.addTextItem().setTitle('Name and surname'),
    attending:   form.addMultipleChoiceItem().setTitle('Are you able to attend?').setChoiceValues([YES, NO]),
    email:       form.addTextItem().setTitle('Email address'),
    dietary:     form.addParagraphTextItem().setTitle('Dietary requirements'),
    plusName:    form.addTextItem().setTitle('Name and surname of plus one'),
    plusEmail:   form.addTextItem().setTitle('Email address of plus one'),
    plusDietary: form.addParagraphTextItem().setTitle("Plus one's dietary requirements"),
    other:       form.addParagraphTextItem().setTitle('Anything else we need to know, or any questions?')
  };

  // Replies land in a Google Sheet
  var sheet = SpreadsheetApp.create('Jack & Lucy — RSVPs');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, sheet.getId());

  // Tidy both into the wedding folder, if there is one
  var folders = DriveApp.getFoldersByName(DRIVE_FOLDER_NAME);
  if (folders.hasNext()) {
    var folder = folders.next();
    DriveApp.getFileById(form.getId()).moveTo(folder);
    DriveApp.getFileById(sheet.getId()).moveTo(folder);
  }

  // Google doesn't expose the "entry.123" field codes directly; a pre-filled
  // link contains them, in question order.
  var keys = Object.keys(items);
  var draft = form.createResponse();
  keys.forEach(function (k) {
    var item = items[k];
    var type = item.getType();
    var r = type === FormApp.ItemType.MULTIPLE_CHOICE ? item.asMultipleChoiceItem().createResponse(YES)
          : type === FormApp.ItemType.PARAGRAPH_TEXT  ? item.asParagraphTextItem().createResponse('x')
          : item.asTextItem().createResponse('x');
    draft.withItemResponse(r);
  });
  var codes = draft.toPrefilledUrl().match(/entry\.\d+/g);
  if (!codes || codes.length !== keys.length) {
    throw new Error('Could not read the field codes. Pre-filled link: ' + draft.toPrefilledUrl());
  }

  var entries = keys.map(function (k, i) { return '      ' + k + ': "' + codes[i] + '"'; }).join(',\n');
  var action = form.getPublishedUrl().replace(/\/viewform.*$/, '/formResponse');

  Logger.log(
    '\n\n===== Paste this into index.html, replacing the existing RSVP_GOOGLE_FORM block =====\n\n' +
    '  var RSVP_GOOGLE_FORM = {\n' +
    '    action: "' + action + '",\n' +
    '    entries: {\n' + entries + '\n    },\n' +
    '    yes: ' + JSON.stringify(YES) + ',\n' +
    '    no: ' + JSON.stringify(NO) + '\n' +
    '  };\n\n' +
    '===== Replies will appear in: ' + sheet.getUrl() + ' =====\n'
  );
}
