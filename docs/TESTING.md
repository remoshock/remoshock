# Pre release testing guide

Testing instruction before release.

<table border="1">

<tr>
<th>No</th>
<th>Action</th>
<th>Result</th>
</tr>


<tr>
<td>1.</td>
<td>Run <code>git status</code></td>
<td>No uncommited changes.</td>
</tr>


<tr>
<td>2.</td>
<td>Increase version number in <code>src/pyshock/core/version.py</code></td>
<td>-</td>
</tr>


<tr>
<td>3.</td>
<td>Run <code>./dist.sh</code></td>
<td>

- No error message
- File `build/pyshock/pyshock-x.x.zip` is created
- <code>git diff</code> shows only modification of the version number, and in REAME.md and version.py only.

</tr>


<tr>
<td>4.</td>
<td>

~~~~
rm ~/.config/pyshock.ini
cd /tmp
unzip ~/workspace/pyshock/build/pyshock-*
cd pyshock
./pyshockcli.py
~~~~

</td>
<td>

- "Please edit pyshock.ini and add an entry sdr=... in the [global] section."
- In pyshock.ini, the variables web_authentication_token and transmitter_code contain random values.
- There is an example configuration for multiple receivers.
- There is an example configuration for th randomizer.
</td>
</tr>


<tr>
<td>5.</td>
<td>Edit pyshock.ini and set sdr=hackrf</td>
<td>-</td>
</tr>


<tr>
<td>6.</td>
<td>Reset PAC receiver into learning mode<br>
Run <code>./pyshockcli.py</code></td>
<td>Receiver was paired to the new transmitter code, it stopped flashing red and started to blink green.</td>
</tr>


<tr>
<td>7.</td>
<td>Run <code>./pyshockcli.py --sdr hackrfcli</code></td>
<td>The receiver beeps.</td>
</tr>


<tr>
<td>8.</td>
<td>Run <code>./pyshockserver.py</code><br>
Open the displayed URL in a web-browser.</td>
<td>The remote-control website is shown.</td>
</tr>


<tr>
<td>9.</td>
<td>Click the BEEP-icon for the first receiver</td>
<td>The receiver beeps.</td>
</tr>


<tr>
<td>10.</td>
<td>Set duration to 1000ms and click the BEEP-SHOCK-icon for the first receiver.</td>
<td>The receiver beeps, there is a delay of 1 second, before the LIGHT flashes for another second.</td>
</tr>


<tr>
<td>11.</td>
<td>End the pyshockserver-process by pressing <code>ctrl+c</code></td>
<td>No error message is shown. No traceback is shown.</td>
</tr>


<tr>
<td>12.</td>
<td>Edit pyshock.ini to setup the following randomizer configuration:

~~~~
[randomizer]
beep_probability_percent = 100
shock_probability_percent = 100
shock_min_duration_ms = 250
shock_max_duration_ms = 500
shock_min_power_percent = 5
shock_max_power_percent = 10
pause_min_s = 3
pause_max_s = 5
start_delay_min_minutes = 0
start_delay_max_minutes = 1
runtime_min_minutes = 2
runtime_max_minutes = 3

~~~~
</td>
<td>-</td>
</tr>


<tr>
<td>13.</td>
<td>Run <code>pyshockrnd.py --mock</code></td>
<td>

- A beep is sent to 4 collars, about a second apart.<br>
- After the last beep and before the first BEEPSHOCK, there is a delay of less than 65 seconds<br>
- There are BEEPSHOCK-message for all 4 collars
- Power varies between 5% and 10%
- Duration varies between the two exact values 250ms and 500ms
- The last BEEPSHOCK-message is between 120s and 185ms of the first BEEPSHOCK-message
- The programm ends with "Runtime comleted".
</td>
</tr>

</table>

# Publish release

- create GitHub-releases with change-notes, a tag starting with "v" followed by the version number
- upload build/pyshock-x.x.zip to the release

~~~~
git commit -am "released version x.x"
git push
git checkout -b VERSION_xx_RELEASE_xx
git push --set-upstream VERSION_xx_RELEASE_xx
git checkout master
~~~~

