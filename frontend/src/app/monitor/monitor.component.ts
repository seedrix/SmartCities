import { Component, OnInit } from '@angular/core';
import { ShopsService } from '../services/shops.service';
import { NavbarService } from '../services/navbar.service';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-monitor',
  templateUrl: './monitor.component.html',
  styleUrls: ['./monitor.component.scss']
})
export class MonitorComponent implements OnInit {
  historyUrl: string;

  public chartDatasets: Array<any> = [{
    data: [0],
    label: 'No data from backend.',
  }];

  public chartLabels: Array<any> = [];

  public chartColors: Array<any> = [
    {
      backgroundColor: [
        'rgba(54, 162, 235, 0.2)',
        'rgba(54, 162, 235, 0.2)',
        'rgba(54, 162, 235, 0.2)',
        'rgba(54, 162, 235, 0.2)',
        'rgba(54, 162, 235, 0.2)',
        'rgba(54, 162, 235, 0.2)',
      ],
      borderColor: [
        'rgba(54, 162, 235, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(54, 162, 235, 1)',
      ],
      borderWidth: 2,
    },
    {
      backgroundColor: [
        'rgba(255, 99, 132, 0.2)',
        'rgba(255, 99, 132, 0.2)',
        'rgba(255, 99, 132, 0.2)',
        'rgba(255, 99, 132, 0.2)',
        'rgba(255, 99, 132, 0.2)',
        'rgba(255, 99, 132, 0.2)',
      ],
      borderColor: [
        'rgba(255,99,132,1)',
        'rgba(255,99,132,1)',
        'rgba(255,99,132,1)',
        'rgba(255,99,132,1)',
        'rgba(255,99,132,1)',
        'rgba(255,99,132,1)',
      ],
      borderWidth: 2,
    }
  ];

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
    let currentData = []
    let maxData = []
    let labels = []

    for (let key in this.shops.shopMap) {
      try {
        const response: any = await this.http.get(this.historyUrl + key).toPromise();
        let id = response.payload.shop_id
        let name = this.shops.shopMap[id].name
        maxData.push(this.shops.shopMap[id].maxPeople)
        console.log(maxData)
        currentData.push(response.payload.count)
        labels.push(name)
      } catch (error) {
        console.log("Error Status: " + error.status)
        console.log(error)
        this.snackbar.open("Could not show values for shop: " + this.shops.shopMap[key].name, "", {
          duration: 3000,
        });
      }
    }
    this.chartLabels = labels;

    this.chartDatasets = [{
      data: currentData,
      label: 'Current number of customers.',
    }, {
      data: maxData,
      label: 'Maximum number of customers.',
    }];

    
  }

  ngOnInit(): void {
  }

  public chartOptions: any = {
    responsive: true,
    scales: {
      yAxes: [{
          ticks: {
              beginAtZero: true
          }
      }]
  }
  };
  public chartClicked(e: any): void { }
  public chartHovered(e: any): void { }

}
