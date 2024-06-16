$(document).ready(function() {
    $('#search-form').on('submit', function() {
        $(this).find('button[type="submit"]').prop('disabled', true).text('Searching...');
    });

    $('form[action="/summarize"]').on('submit', function() {
        $(this).find('button[type="submit"]').prop('disabled', true).text('Summarizing...');
    });
});
