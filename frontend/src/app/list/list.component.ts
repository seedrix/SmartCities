import { Component, OnInit } from '@angular/core';
import { ShopsService } from '../services/shops.service';

@Component({
  selector: 'app-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.scss']
})
export class ListComponent implements OnInit {  

  constructor(public shops: ShopsService) { }

  ngOnInit(): void {
  }

}
