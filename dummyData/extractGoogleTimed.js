function extractDay(div){
    var a = div.getElementsByClassName("lubh-bar")
    //console.log(a)
    //console.log(a.length);
    var arrayLength = a.length;
    var times = []
    for (var i = 0; i < arrayLength; i++) {
    var h = a[i].style.getPropertyCSSValue('height').cssText.match(/[0-9]+/g)[0]
    var t = a[i].getAttribute("aria-label").substring(0,2)
        //console.log(t);
        times.push({'height':h, 'time':t})
        //Do something
    }
    console.log(times)
    for (var i = 0; i < arrayLength; i++) {
     var b = times[i]
     var st = JSON.stringify({})
    // console.log(st+',')
    }
    return times
    }
    
    var c = document.getElementsByClassName("yPHXsc")
    var week = []
    for (var i = 0; i < c.length; i++) {
     var times = extractDay(c[i])
     var day = c[i].parentNode.getAttribute("aria-label")
     console.log(day)
     week.push({'weekday':i, 'times':times})
    }
    console.log(JSON.stringify(week))