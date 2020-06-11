// Your web app's Firebase configuration
var firebaseConfig = {
    apiKey: "API_KEY",
    authDomain: "AUTH_DOMAIN",
    databaseURL: "DB_URL",
    projectId: "FIREBASE_PROJECT_ID",
    storageBucket: "BUCKET_URL",
    messagingSenderId: "SENDER_ID",
    appId: "APP_ID"
  };

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

const database = firebase.database();

database.ref('latest').on('child_added', function(data) {

  let tweet = data.val();
  let currentScore = tweet.score;

  $('#latest-tweet').fadeOut();
  $('#latest-tweet').html('');
  $('#latest-tweet').fadeIn();
  $('.tweet-text').text(tweet.text);


  // Adjust the sentiment scale for the latest tweet
  let scaleWidthPx = 400; // width of our scale in pixels
  let scaledSentiment = (scaleWidthPx * (currentScore + 1)) / 2;
  $('#current-sentiment-latest-val').css('margin-left', scaledSentiment + 'px');

});
