# SEDS induction tasks

## Task 1

- The first time I read this task, I was quite sleepy, so wasn't really sure how hard it was. The second time I read this I was far more clear on how to attempt it.

- For context, I've been programming for some time now, and I'm decently sure of how to do dataviz and some of the methods involved in sanitation and data visualisation, so writing the code wasn't really the largest problem for me.

- I've recently been doing quite a lot of ML, so for smoothing noise and other general things, you typically go with Exponentially weighted moving average algos. So for the string type error, I just forced it to Nan, and then for spikes or random noise in the data, we have to handle them differently.

- If you get the spikes into the ewma,it'll spoil everything so I was thinking of how to handle that.

- Came up with a two filter solution -> first thought was Kalman, but then way too overkill; so just a median filter to get the very big spikes out of the way, and then smoothed noise with the ewma.

- Apart from this, I display the actual sensor values in gray with lower opacity so you can actually see what's coming in, and then the smoothed version on top. I also have red dots for where the depth is rapidly reducing.

- Implemented a speed multiplier for the animation because debugging at the speed the task required was just extremely annoying.

![graph image](<./Joshua Daniel_2026AAPS0234H_Avionics_graph.png>)

<center>graph picture</center><br>

![graph gif](<./Joshua Daniel_2026AAPS0234H_Avionics_graph_video.gif>)

<center>graph gif</center><br>

- The auto button seen at the end is for automatic movement of the moving data, because you'd not be interested in historical accumulation of data, rather what's to come with some history; though you can manually override it.

- I tried reaching out to somebody who was in Janus whom I met in the mess randomly to ask for feedback regarding the filtering algorithms I was doing, but then they said, "ask somebody else in the group". I also tried reaching out when there was an enormous group discussion in Mess 1, where I was rightfully again, asked to leave because whatever was happening was quite important, but I'm quite sure I've done this task to a decently satisfactory level.

- If I had to find a flaw: probably not using a full fledged GUI and not structuring the button properly, plus colour of sliders aren't particularly great. moreover, the proximity alert should be called surface closer alert.

## Task 2

[tinkercad link](https://www.tinkercad.com/things/60DVyR8AIkK/editel?sharecode=oZRcVe0A3lb6DrV5xS7yBAlS3EcT1fiSsEhAbKnxlq0)

- Where do I even start? I already have minimal experience with electronics in particular to begin with, so tone down your expectations a notch in comparison to the first project.

- Most of the components you've mentioned are quite straightforward, and so is the coding part too. The precedence wasn't particularly hard to figure out, I guess there was somewhat arbitrary choice anyway.

![schematic](<./Joshua Daniel_2026AAPS0234H_Avionics_schematic.png>)

<center>schematic</center><br>

![schematic](<./Joshua Daniel_2026AAPS0234H_Avionics_arduino_wiring.png>)

<center>wiring: relatively clean I hope</center><br>

- The only major pain point of mine was that while the programming task I had enough proficiency ( if you look at the repo, you'll see that I first committed the depth data two weeks ago, and only then did I start to actually work on my tasks), to complete it within ~3 hours for the proper final end; the wiring for this was what particularly mundane to me.

- Not to mention that the task was quite meticulous in specifying every other component in excruciating detail, but then completely missed the point of specifying what exactly I should use as the light sensor.

- In hindsight, this is most likely me overcomplicating it myself, but I've been working on research in photodetectors for a while now, so the photodiode in reverse bias, and the photores also made sense to me. It was some kind of decision paralysis. This was when I reached out for help, and I was told to go with the ambient light sensor.

- I can rationalise this choice in the following manner, what we're essentially doing is tracking light disappearance, so ambient light sensing would be the best to do this.

- In my hobbyist experiments with NodeMCUs, I've used everything but the ambient light sensor and LCDs (now you have a decent measure of how well I've done hobbyist experiments) so I had decent exp with wiring up everything except this, and had to actually learn about potentiometer wiper contrast, and the pull down res for the ambient light sensing of course.

- If I had to point out a flaw: in my execution it would probably be me hardcoding in the half-slider value for the light sensor, because I know its logarithmic (which I learnt relatively recently, matter of fact), and it also depends on the value of the pull-down res, but I just serial printed the values until it got relatively close to half (this was at 3 in the morning, on a day where I had classes); and then hardcoded in the value.

## Miscellaneous

- You might not see a lot of commits, that's because even though I am a relatively serious developer, I guess there's some issues with gh configuration on my machine, and I've been quite busy with competitive coding and other acads related stuff to set this up.

- This is not particularly indicative of my development hygiene. I am, atleast for the most part, somewhat discplinary in terms of following the typical commit formats, but for this project and this execution, it took the air out of me, so please forgive most of the changes in one commit.

- I thought to add a video of both the graph and the simulation, and will do so at the earliest possible moment, but just in case that's not in time, I want this finalised in submission.
