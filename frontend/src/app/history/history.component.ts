import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ShopsService } from '../services/shops.service';
import { MatSnackBar } from '@angular/material/snack-bar';


@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.scss']
})
export class HistoryComponent implements OnInit {
  historyUrl: string;

  public chartDatasets: Array<any> = [{
    data: [0],
    label: "No data available.",
  }];

  public chartLabels: Array<any> = ["No data available."];

  ngOnInit(): void {

  }

  constructor(private http: HttpClient, private shops: ShopsService, private snackbar: MatSnackBar) {
    this.historyUrl = this.shops.url + "shops/people/";

    if (Object.keys(shops.shopMap).length != 0) {
      this.getData()
    } else {
      this.shops.shopsInit.subscribe(value => {
        if (value) {
          this.getData()
        }
      })
    }



  }

  private async getData() {
    // this.chartDatasets = []
    const showFutureData = false;
    const axisTicksInterval = 2;

    let date = this.getDate()

    const timestamps = new Set();
    const shopsData = {};
    const timestampNow = Math.floor(Date.now() / 1000);
    for (let key in this.shops.shopMap) {
      try {
        const response: any = await this.http.get(this.historyUrl + key + '/' + date).toPromise();

        const shopData = {};
        response.forEach(element => {
          if (showFutureData === false && timestampNow <= element.timestamp){
            return;
          }
          shopData[element.timestamp] = element.payload.count;
          timestamps.add(element.timestamp);
        });
        shopsData[key] = shopData;

      } catch (error) {
        console.log('Error Status: ' + error.status)
        console.log(error)
        this.snackbar.open('Could not show values for shop: ' + this.shops.shopMap[key].name, '', {
          duration: 3000,
        });
      }
    }

    const chartData = [];
    const labels = [];
    const shopsDataNormalized = {};
    for (const key in this.shops.shopMap) {
      shopsDataNormalized[key] = [];
      chartData.push({
        data: shopsDataNormalized[key],
        xAxisID: 'datetime',
        label: this.shops.shopMap[key].name,
      });
    }
    const sortedTimestamps = Array.from(timestamps);
    sortedTimestamps.sort();
    let lastTimestamp = new Date(0);
    const dateDayFormatter = new Intl.DateTimeFormat('en-DE', {weekday: 'short', day: '2-digit', month: '2-digit', year: '2-digit'});
    sortedTimestamps.forEach(timestamp => {
      const thisDate = new Date(Number(timestamp) * 1000);
      let suffix = '';
      if (lastTimestamp.toLocaleDateString() !== thisDate.toLocaleDateString()) {
        suffix = ';';
      }
      lastTimestamp = thisDate;
      labels.push(dateDayFormatter.format(thisDate) + '; ' + thisDate.getHours() + suffix);

      for (const key in this.shops.shopMap) {
        if (timestamp in shopsData[key]) {
          shopsDataNormalized[key].push(shopsData[key][timestamp]);
        } else {
          shopsDataNormalized[key].push(null);
        }
      }
    });

    this.chartDatasets = chartData;
    this.chartLabels = labels;
    this.chartOptions = {
      responsive: true,
      scaleShowValues: true,
      scales: {
        xAxes: [
          {
            id: 'clock',
            ticks: {
              callback: (label, index)  => {
                if (index % axisTicksInterval === 0){
                  return label.split(';')[1];
                }
                return null;
              }
            }
          },
          {
            id: 'date',
            ticks: {
              autoSkip: false,
              callback: (label, index) => {
                const split = label.split(';');
                if (split.length === 3) {
                  return split[0];
                }
                return null;
              }
            },
            gridLines: {
              lineWidth: 2,
              color: 'rgba(0, 150, 0, 0.4)'
            }
          },
          {
            id: 'datetime',
            ticks: {
              display: false
            },
            gridLines: {
              display: false,
              color: 'rgba(0, 0, 0, 0)',
              lineWidth: 0.001
            }
          }]}

    };

  }

  private getDate() {
    let date = new Date()
    // current day
    date.setHours(0)
    date.setMinutes(0)
    date.setSeconds(0)
    console.log(date)

    // 2 weeks
    date.setDate(date.getDate()-7);
    date.setMinutes(0)
    date.setSeconds(0)


    let timestamp = Math.floor(+date / 1000)
    console.log(timestamp)
    return timestamp

  }


  public chartType: string = 'line';




  public chartOptions: any = {
    responsive: true
  };
  public chartClicked(e: any): void { }
  public chartHovered(e: any): void { }


}
