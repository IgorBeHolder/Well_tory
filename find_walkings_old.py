def find_walkings(df, pace_min = 0.5, pace_max = 2, min_session = 300, max_pause = 15):
    '''
    Return a dictionary with a structure as follows:
        
    {
        "<day yyyy-mm-dd>": [  # list of walkings had taken that day
            {
                "start": "<yyyy-mm-dd HH:MM:SS>”,
                "end": "<yyyy-mm-dd HH:MM:SS>",
                "steps": <int>
            },
            …
        ]
    }

        Parameters
        ----------
        pace_min : Minimum pace rate during walking (steps per second).
        pace_max : Maximum pace rate during walking (steps per second).
        min_session: Minimum time to consider the session as a single 
                    walking activity (in seconds).
        max_pause: Maximum pause between records to merge into
                   a single walking activity (in seconds).

        Returns
        -------
        Dictionary.

        Output dictionary is written as a byte stream using python "pickle" library 
        to "walkings.json" file to default local folder.


    '''
    walkings = {}
    day_list = []
    pause = 0
    next_r = 0

    for r in range(len(df)):

        # skip rows we have already read (if next_r > r)
        if next_r == r:

            # merge intervals with acceptable gaps ( < max_pause )

            # current row duration (interval)
            t_int = (df['time_end_local'].loc[r] - df['time_start_local'].loc[r])\
                    .total_seconds()
            steps = df['steps'].loc[r]

            # lookup for next row
            next_r = r + 1
            while next_r < len(df):
                
                # pause between rows (intervals)
                pause = (df['time_start_local'].loc[next_r] - \
                            df['time_end_local'].loc[next_r-1]).total_seconds()
                
                # if next interval starts before previous ends
                if pause < 0:
                    break

                # if pause is acceptable
                if  pause  < max_pause:
                    #  print(f'row:{r}  next_r:{next_r} pause:{pause}  t_int:{t_int}   steps:{steps}')

                    # new interval value 
                    t_int = (df['time_end_local'].loc[next_r] - df['time_start_local']\
                             .loc[r]).total_seconds()  
                    steps += df['steps'].loc[next_r]
                else:
                    
                    break
                
                next_r += 1


            # we have a merged data now
            

            if t_int >= min_session and  pace_min < steps/t_int < pace_max:

                                  
                current_day = df['time_start_local'].loc[r].strftime("%Y-%m-%d")

                # test for a DAY key
                if current_day not in walkings:

                    day_list = []
                    walkings.setdefault(current_day)
                    walkings[current_day] = day_list

                start = df['time_start_local'].loc[r].strftime(dateformat)

                # !!! next_r-1 index
                end = df['time_end_local'].loc[next_r-1].strftime(dateformat)

                walkings[current_day].append(
                                        {'start':start,
                                        'end':end,
                                        'steps':steps,
                                        # 'pace': round(steps / t_int, 1)
                                        }
                                        )
    # write as bytes stream
    with open('walkings.json', 'wb') as f:
        pickle.dump(walkings, f)
    f.close()  

    return walkings