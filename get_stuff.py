import pandas as pd
import cv2
import os
import glob
import math

def get_position(x, y):
	x = min(max(x, -7620), 7620)
	y = min(max(y, -14325.6), 14325.6)

	x = int((x + 7620) * (612 - 20) / (7620 * 2)) + 10
	y = int((y + 14325.6) * (1080 - 20) / (14325.6 * 2)) + 10

	# print(x, y)
	assert x >= 0
	assert y >= 0

	return x, y

def get_distance(player, hoop):
	return math.sqrt((player[0] - hoop[0][0])** 2 + (player[1] - hoop[0][1]) ** 2)

def get_slope(pt1, pt2):
	m = (pt1[0] - pt2[0]) / (pt1[1] - pt2[1])
	b = pt1[0] - m * pt1[1]

	return m, b


# Only doing men's games
games = glob.glob('timeseries/M_*')

# game = 'M_17472065-4ad8-11ea-9084-0242bdc61da9'
court_template = cv2.imread('images/basketballcourt_lines.png')

games = [os.path.basename(g) for g in games]

players = []
all_reb = []

# >>> df = pd.DataFrame()
# >>> data = pd.DataFrame({"A": range(3)})
# >>> df.append(data)

rows = []

for game in games:

	play_by_play = pd.read_csv('playbyplay/{}.csv'.format(game))
	# ball_location = pd.read_csv('timeseries/{}/{}_ballLocations.csv'.format(game, game))
	# player_location = pd.read_csv('timeseries/{}/{}_playerLocations.csv'.format(game, game))
	player_location = pd.read_csv('timeseries/{}/{}_playerPossession.csv'.format(game, game))
	shots = pd.read_csv('timeseries/{}/{}_shots.csv'.format(game, game))

	# print(player_location.columns)

	# def_rebound = play_by_play.loc[play_by_play['DEFENSIVE_REB'] == 1.0]
	# off_rebound = play_by_play.loc[play_by_play['OFFENSIVE_REB'] == 1.0]
	rebounds = play_by_play.loc[(play_by_play['REB'] == 1.0)]

	# print(rebounds['PlayerId'])

	hoops = []

	for hoop in shots['hoopID'].unique():
		h = shots.loc[shots['hoopID'] == hoop].iloc[0]
		hoops.append([get_position(h['hoopX'], h['hoopY'])])

		# cv2.circle(court_template, (y, x), 5, [0,255,0], -1)

	for index, row in rebounds.iterrows():
		time = row['Timestamp']

		possession = player_location.loc[(player_location['timestamp'] >= (time - 3000)) & (player_location['timestamp'] <= (time + 100))]
		# shot = shots.loc[(shots['timestamp'] >= (time - 4000)) & (shots['timestamp'] <= time)]

		if row['PlayerId'] == 0:
			print('team rebound')
		
		if possession.shape[0] == 0:
			print('here') # No possession associated, ignore
		else:
			# print(possession['playerID'].values[-1] == row['PlayerId']) # idk
			# print(possession['X'].values[-1], possession['Y'].values[-1])
			x, y = get_position(possession['X'].values[-1], possession['Y'].values[-1])

			players.append(possession['playerID'].values[-1])

			# print(possession['X'].values[-1], possession['Y'].values[-1])
			# print(x, y)

			# print(hoops)

			if hoops[0][0][1] < hoops[1][0][1]:
				hoops0 = hoops[0]
				hoops1 = hoops[1]

				hoop1 = get_distance([x, y], hoops0)
				hoop2 = get_distance([x, y], hoops1)

				if hoop1 > hoop2:
					x, y = get_position(possession['X'].values[-1], -1 * possession['Y'].values[-1])
					hoop1 = hoop2
			else:
				hoops0 = hoops[0]
				hoops1 = hoops[1]
				hoops[0] = hoops[1]

				hoop1 = get_distance([x, y], hoops0)
				hoop2 = get_distance([x, y], hoops1)

				# if hoop2 > hoop1:
				x, y = get_position(possession['X'].values[-1], -1 * possession['Y'].values[-1])
				# hoop1 = hoop2

			pt1, pt2 = ((hoops[0][0][1], hoops[0][0][0]), (hoops[0][0][1] + 70, 10))
			m1, b1 = get_slope(pt1, pt2)

			pt3, pt4 = ((hoops[0][0][1], hoops[0][0][0]), (hoops[0][0][1] + 600, 10))
			m2, b2 = get_slope(pt3, pt4)

			pt5, pt6 = ((hoops[0][0][1], hoops[0][0][0]), (hoops[0][0][1] + 600, 602))
			m3, b3 = get_slope(pt5, pt6)

			pt7, pt8 = ((hoops[0][0][1], hoops[0][0][0]), (hoops[0][0][1] + 70, 602))
			m4, b4 = get_slope(pt7, pt8)

			if y < m1 * x + b1 and x < hoops[0][0][0]:
				# cv2.circle(court_template, (y, x), 5, [255,0,0], -1) # blue
				if hoop1 < (1829 * 592 / (7620 * 2)):
					cv2.circle(court_template, (y, x), 5, [255,0,0], -1) # blue
					row['class'] = 5
				elif hoop1 < (4572 * 529 / (7620 * 2)):
					cv2.circle(court_template, (y, x), 5, [255,0,255], -1)
					row['class'] = 10
				else:
					cv2.circle(court_template, (y, x), 5, [125, 125, 0], -1)
					row['class'] = 15
			elif y < m2 * x + b2 and x < hoops[0][0][0]:
				# cv2.circle(court_template, (y, x), 5, [255,0,0], -1) # blue
				if hoop1 < (1829 * 592 / (7620 * 2)):
					cv2.circle(court_template, (y, x), 5, [255,125,0], -1) # blue
					row['class'] = 4
				elif hoop1 < (4572 * 529 / (7620 * 2)):
					cv2.circle(court_template, (y, x), 5, [255,125,255], -1)
					row['class'] = 9
				else:
					cv2.circle(court_template, (y, x), 5, [125, 125, 125], -1)
					row['class'] = 14
			elif y < m3 * x + b3:
				# cv2.circle(court_template, (y, x), 5, [255,0,0], -1) # blue
				if hoop1 < (1829 * 592 / (7620 * 2)):
					cv2.circle(court_template, (y, x), 5, [50,125,0], -1) # blue
					row['class'] = 2
				elif hoop1 < (4572 * 529 / (7620 * 2)):
					cv2.circle(court_template, (y, x), 5, [50,125,255], -1)
					row['class'] = 7
				else:
					cv2.circle(court_template, (y, x), 5, [125, 50, 125], -1)
					row['class'] = 12
			else:
				if hoop1 < (1829 * 592 / (7620 * 2)):
					cv2.circle(court_template, (y, x), 5, [75,123,0], -1) # blue
					row['class'] = 3
				elif hoop1 < (4572 * 529 / (7620 * 2)):
					cv2.circle(court_template, (y, x), 5, [50,125,97], -1)
					row['class'] = 8
				else:
					cv2.circle(court_template, (y, x), 5, [125, 65, 125], -1)
					row['class'] = 13
			if y < m4 * x + b4 and x > hoops[0][0][0]:
				# cv2.circle(court_template, (y, x), 5, [255,0,0], -1) # blue
				if hoop1 < (1829 * 592 / (7620 * 2)):
					cv2.circle(court_template, (y, x), 5, [45,45,129], -1) # blue
					row['class'] = 1
				elif hoop1 < (4572 * 529 / (7620 * 2)):
					cv2.circle(court_template, (y, x), 5, [50,125,75], -1)
					row['class'] = 6
				else:
					cv2.circle(court_template, (y, x), 5, [125, 7, 125], -1)
					row['class'] = 11

			cv2.circle(court_template, (hoops[0][0][1], hoops[0][0][0]), 5, [0,255,0], -1)
			cv2.circle(court_template, (hoops[0][0][1] + 70, 10), 5, [0,255,0], -1)
			cv2.line(court_template, (hoops[0][0][1], hoops[0][0][0]), (hoops[0][0][1] + 70, 10), [0,255,0], 5)
			cv2.line(court_template, (hoops[0][0][1], hoops[0][0][0]), (hoops[0][0][1] + 600, 10), [0,255,0], 5)
			cv2.line(court_template, (hoops[0][0][1], hoops[0][0][0]), (hoops[0][0][1] + 600, 602), [0,255,0], 5)
			cv2.line(court_template, (hoops[0][0][1], hoops[0][0][0]), (hoops[0][0][1] + 70, 602), [0,255,0], 5)
			cv2.line(court_template, (hoops[0][0][1], hoops[0][0][0]), (0, hoops[0][0][0]), [0,255,255], 5)

			row['game'] = game

			all_reb.append(time)
			rows.append(row)

			# if shot
			# if len(shot) != 0:
			# 	print(shot['playerID'].values[-1])


	# print(possession['X'])
	# print(possession['Y'])

	# break

	# assert possession.shape[0] > 0

# 	x_ball, y_ball = get_position(ball_location.loc[(ball_location['timestamp'] <= (time + 4)) & (ball_location['timestamp'] >= time - 4)]['X'].values[0],
# 		ball_location.loc[(ball_location['timestamp'] <= (time + 4)) & (ball_location['timestamp'] >= time - 4)]['Y'].values[0])

# 	print(ball_location.loc[(ball_location['timestamp'] <= (time + 4)) & (ball_location['timestamp'] >= time - 4)].shape)

# 	x, y = get_position(player_location.loc[(player_location['timestamp'] <= (time + 4)) & (player_location['timestamp'] >= time - 4)]['X'].values[0],
# 		player_location.loc[(player_location['timestamp'] <= (time + 4)) & (player_location['timestamp'] >= time - 4)]['Y'].values[0])
# 	cv2.circle(court_template, (x_ball, y_ball), 5, [0,255,0], -1)

	# break

cv2.imshow('court', court_template)
cv2.waitKey()

cv2.imwrite('training.png', court_template)

# print(len(set(players)))
print(len(all_reb))

pd.DataFrame(rows).to_csv('rebounds.csv')
