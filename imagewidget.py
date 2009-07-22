#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *
from PyKDE4.kio import KIO

class ThumbnailView(QWidget):

    def __init__(self, api_url, cache, parent):

        #FIXME: Pass a dictionary of parameters, much better
        super(ThumbnailView, self).__init__(parent)
        
        self.api_url = api_url
        self.urls = list()
        self.cache = cache
        self.column_index = 0
        self.max_row_items = 3
        self.row_index = 0

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

    def get_api(self):
        tempfile = KTemporaryFile()
        if tempfile.open():
            flags = KIO.JobFlags(KIO.Overwrite | KIO.HideProgressInfo)
            job = KIO.file_copy(KUrl(self.api_url),
                                KUrl(tempfile.fileName()), -1, flags)
            job.ui().setWindow(self)
            if KIO.NetAccess.synchronousRun(job, self):
                self.get_preview_urls(job)
    
    def get_preview_urls(self):
    
        dest_url = job.destUrl()
        api_response = open(dest_url.path())
        values = json.load(api_response)
        for item in values:
            url = item["preview_url"]
            self.urls.append(url)
        self.urls = [KUrl(item) for item in self.urls]
        KIO.NetAccess.removeTempFile(dest_url.path())

    def insert_items(self, widget):

        if self.column_index >= self.max_row_items:
            self.row_index += 1
            self.column_index = 0
        self.layout.addWidget(widget, self.row, self.column_index)

    def create_image_label(self, image=None, pixmap=None):
        
        label = QLabel()
        pixmap = QPixmap.fromImage(image) if not pixmap else pixmap
        
        if pixmap.isNull():
            return
        
        label.setPixmap(pixmap)
        return label
          
    def retrieve_thumbnails(self):
        
        for url in self.urls:
            name = url.fileName()
            pixmap = QPixmap()

            if not self.cache.find(name, pixmap):
                tempfile = KTemporaryFile()

                if tempfile.open():
                    flags = KIO.JobFlags(KIO.Overwrite | KIO.HideProgressInfo)
                    job = KIO.file_copy(KUrl(url), KUrl(tempfile.fileName()),
                                        -1, flags)
                    job.ui().setWindow(self)
                    
                    if KIO.NetAccess.synchronousRun(job, self):
                        self.process_thumbnails(job)
                        KIO.NetAccess.removeTempFile(tempfile.fileName())
            else:
                self.setCentralWidget(self.area)
                label = create_image_label(pixmap=pixmap)
                if label is not None:
                    self.insert_items(label)

    def process_thumbnails(self, job):

        img = QImage()
        dest = job.destUrl()
        img.load(dest.path())

        if not img.isNull():

            label = create_image_label(image=img)
            
            if label is not None:
                self.insert_items(label)
                name = job.srcUrl().fileName()
                      
                if not self.cache.find(name, pixmap):
                    self.cache.insert(name, pixmap)

        time.sleep(1) #TODO: Make configurable
