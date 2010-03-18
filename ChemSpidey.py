#!/usr/bin/env python
#
#!/usr/bin/python2.4
#
# 
"""ChemSpidey - a Chemistry robot for Wave.

Gives you the an image of a named chemical for text in a blip. Heavily dependant on
'Grauniady' the Guardian API Robot written by Chris Thorpe. Version 2 draws on
inspiration from the Pirate Selection Translater by Google.
"""

__author__ = 'cameron.neylon@stfc.ac.uk (Cameron Neylon)'

import logging
from waveapi import events
from waveapi import ops
from waveapi import element
from waveapi import robot
from waveapi import appengine_robot_runner

from ChemSpideyUtil import *

CHEM_KEY = "ChemSpidey.appspot.com/todo"

def OnAnnotationChanged(event, wavelet):
  """Identify annotations that match CHEM_KEY and return modified text and anntns

  Collects a list of annotations, which are already matched in the registered handler
  then sends the annotated text to chemify which returns new text with annotations. 
  It then sends it back to the wave with links and annotations"""

  blip = event.blip
  text = blip.text

  # construct a list of annotations to translate into chemistry. 
  # this needs to be outside the loop for modification
  todo = []

  # collect up start, end, and values of annotations that match CHEM_KEY
  for ann in blip.annotations:
    if ann.name == CHEM_KEY:
      todo.append([ann.start, ann.end, ann.value])

  # reverse the order of todo to reduce the risk of positions of the annotation
  # changing during the course of the operation of the robot
  todo.reverse
 
  # do the actual modifications
  for start, end, value in todo:
    payload = text[start:end]
    chemistry = chemify(payload)

    if 'error' in chemistry:
        blip.append('\n\nError:' + chemistry['replacementtext'])
        blip.range(start, end).clear_annotation(CHEM_KEY)
        return

    # if there is an image url in returned dictionary requested then 
    # replace with image
    if chemistry:
      if payload.find('image') != -1:
        blip.range(start, end).clear_annotation('chemspidey.appspot.com/todo')
        
        blip.range(start, end).replace(element.Image(
          url=chemistry.get('imageurl', 'todo:this needs a failure image url'),
          width = 100, height = 100))

        for annotations in chemistry['annotations']:
          annotation = annotations.get('annotation', None)
          val = annotations.get('value')

          if annotation:
            blip.range(start, (start + 1)).annotate(annotation, value = val)

      # set up the string to replace the existing text from dict returned by chemify
      else:
        chemtext = chemistry.get('replacementtext')
        blip.range(start, end).clear_annotation('chemspidey.appspot.com/todo')
        blip.range(start, end).replace(chemtext)
      
      # annotate the inserted string based on dictionary returned by chemify
        for annotations in chemistry['annotations']:
          annotation = annotations.get('annotation', None)
          val = annotations.get('value', 'no value')
          offset = annotations.get('offset', 0)
          length = annotations.get('length', 0)

          if annotation:
            blip.range(start + offset, start + offset + length
                       ).annotate(annotation, value = val)


def HighLightAnns(event, wavelet):
  """Highlight annotations in different colours when checkbox clicked"""

  blip = event.blip
  highlightcheckbox = blip.first(element.Check, name = 'highlightcheckbox')

  if getattr(highlightcheckbox.value(), 'value') == 'true':
    logging.debug('Checkbox = true')
    for ann in blip.annotations:
      if ann.name == 'chemspidey.appspot.com/role' and ann.value == 'startingmaterial':
        blip.range(ann.start, ann.end).annotate('style/backgroundColor', value = 'blue')
      elif ann.name == 'chemspidey.appspot.com/role' and ann.value == 'reagent':
        blip.range(ann.start, ann.end).annotate('style/backgroundColor', value = 'green')
      elif ann.name == 'chemspidey.appspot.com/role' and ann.value == 'product':
        blip.range(ann.start, ann.end).annotate('style/backgroundColor', value = 'red')
      elif ann.name == 'chemspidey.appspot.com/csid':
        blip.range(ann.start, ann.end).annotate('style/backgroundColor', value = 'yellow')
     
  elif getattr(highlightcheckbox.value(), 'value') == 'false':
    logging.debug('Checkbox = false')
    for ann in blip.annotations:
      if ann.name == 'style/backgroundColor':
        blip.range(ann.start, ann.end).clear_annotation('style/backgroundColor')


def OnWaveletSelfAdded(event, wavelet):
  """Invoked when the robot has been added."""

  logging.info('OnWaveletSelfAdded')
  blip = event.blip
  welcome = blip.reply()
  welcome.append("\nHello I'm ChemSpidey. I'm here to help you markup your chemistry. Select a fragment of text to convert to links to ChemSpider, if you include 'image' an image, linked to ChemSpider will be inserted instead. You can also include weights, volumes, and the keywords, startingmaterial, solvent, reagent, or product and these will be annotated in your text and can be highlighted using the button above\n")
  highlightcheckbox = element.Check('highlightcheckbox')
  blip.append('\n\n\n')
  blip.append(highlightcheckbox)
  blip.append("Highlight annotations?     ")
  highlightbutton = element.Button('highlightbutton', 'Click to Highlight')
  blip.append(highlightbutton)
  OnAnnotationChanged(event, wavelet)

def dodebug(event, wavelet):

  logging.info('DocumentChanged')

if __name__ == '__main__':
  chemspidey = robot.Robot('ChemSpidey',
      image_url='http://www.chemspider.com/ImagesHandler.ashx?id=236',
      profile_url='')
  chemspidey.register_handler(events.AnnotatedTextChanged, 
      OnAnnotationChanged)
  chemspidey.register_handler(events.WaveletSelfAdded, OnWaveletSelfAdded)
  chemspidey.register_handler(events.FormButtonClicked, HighLightAnns)
  appengine_robot_runner.run(chemspidey, debug=True)
