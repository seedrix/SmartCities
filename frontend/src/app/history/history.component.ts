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
    let chartData = []
    let labels = []
    let date = this.getDate()
    for (let key in this.shops.shopMap) {
      try {
        const response: any = await this.http.get(this.historyUrl + key + "/" + date).toPromise();
        let data = []
        let time = []
        
        response.forEach(element => {
          data.push(element.payload.count)
          time.push(element.datetime)
        });

        chartData.push({
          data: data, 
          label: this.shops.shopMap[key].name,
        });

        if (labels.length == 0) {
          labels = time
        }
        
  
      } catch (error) {
        console.log("Error Status: " + error.status)
        console.log(error)
        this.snackbar.open("Could not show values for shop: " + this.shops.shopMap[key].name, "", {
          duration: 3000,
        });
      }
    }

    this.chartDatasets = chartData;
    this.chartLabels = labels
    

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
