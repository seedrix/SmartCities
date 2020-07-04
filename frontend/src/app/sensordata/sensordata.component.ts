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
  historyUrl: string;

  constructor(private http: HttpClient, private shops: ShopsService, private snackbar: MatSnackBar) {
    this.historyUrl = this.shops.url + "shops/people/";
  }


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
    

  }

}
