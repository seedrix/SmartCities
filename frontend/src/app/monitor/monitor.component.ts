import { Component, OnInit } from '@angular/core';
import { ShopsService } from '../services/shops.service';

@Component({
  selector: 'app-monitor',
  templateUrl: './monitor.component.html',
  styleUrls: ['./monitor.component.scss']
})
export class MonitorComponent implements OnInit {


  constructor(public shops: ShopsService) { }

  ngOnInit(): void {
  }

}
