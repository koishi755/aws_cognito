"use strict";

$('.post').on('click', function(){

    //API Gatewayのエンドポイント
    var apiUrl = 'https://e510a0t1eb.execute-api.ap-northeast-1.amazonaws.com/dev';

    //ヘッダー
    var myHeaders = new Headers();
        // add content type header to object
        myHeaders.append("Content-Type", "application/json");

    //渡すデータ
    var raw = JSON.stringify({
        "user_name": $("#user_name").val(),
        "password": $("#password").val(),
        "email": $("#email").val()
    });

    var user_name = $("#user_name").val()

    // create a JSON object with parameters for API call and store in a variable
    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
        redirect: 'follow'
    };

    // make API call with parameters and use promises to get response
    fetch(apiUrl, requestOptions)
    .then(response => response.text())
    .then(result => alert(JSON.parse(result).body))
    .catch(error => console.log('error', error));

    location.href=`https://update-user-profile.s3-ap-northeast-1.amazonaws.com/${user_name}/profile.html`;
});
