import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ShopsService } from '../services/shops.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-sensordata',
  templateUrl: './sensordata.component.html',
  styleUrls: ['./sensordata.component.scss']
})
export class SensordataComponent implements OnInit {

  constructor(private http: HttpClient, private shops: ShopsService, private snackbar: MatSnackBar) { }

  ngOnInit(): void {
    if (Object.keys(this.shops.shopMap).length != 0) {
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

}
