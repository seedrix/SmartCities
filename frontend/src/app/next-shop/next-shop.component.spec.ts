import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { NextShopComponent } from './next-shop.component';

describe('NextShopComponent', () => {
  let component: NextShopComponent;
  let fixture: ComponentFixture<NextShopComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ NextShopComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(NextShopComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
