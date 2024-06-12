import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ClusterViewComponent } from './cluster-view.component';

describe('ClusterViewComponent', () => {
  let component: ClusterViewComponent;
  let fixture: ComponentFixture<ClusterViewComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ClusterViewComponent]
    });
    fixture = TestBed.createComponent(ClusterViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
