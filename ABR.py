
class Algorithm:
    def __init__(self):
    # fill your self params
        self.NUM_LEVELS = 4
        self.BIT_RATE_LEVEL = [500.0, 850.0, 1200.0, 1850.0]
        self.past_decisions = []
        self.past_actual_bitrate = []
        self.past_predicted_bitrate = []
        self.past_N_nst = []
        self.throughput = []
        for i in range(self.NUM_LEVELS):
            newlist = []
            self.past_actual_bitrate.append(newlist)
            self.past_predicted_bitrate.append(newlist)
        self.ERfactor = 3
        self.target_buffer_factor = 0
        self.throughput_factor = 3
        self.beta_factor = 1
        self.Bth = 1
        self.latency_factor = 4

    # Initial
    def Initial(self):
    # Initial your session or something
        self.past_decisions.clear()
        self.past_decisions.append(0)
        self.past_N_nst.clear()
        self.past_N_nst.append(0)
        self.throughput.clear()
        for i in range(self.NUM_LEVELS):
            self.past_actual_bitrate[i].clear()
            self.past_predicted_bitrate[i].clear()
        return 0

    # Define your algo
    def run(self, time, S_time_interval, S_send_data_size, S_chunk_len, S_rebuf, S_buffer_size, S_play_time_len,S_end_delay, S_decision_flag, S_buffer_flag,S_cdn_flag,S_skip_time, end_of_video, cdn_newest_id,download_id,cdn_has_frame,IntialVars):
        if end_of_video:
            # print(sum(self.throughput) / len(self.throughput))
            self.Initial()
            default_bitrate = 0
            default_target_buffer = 0
            default_latency_limit = 4
            return [default_bitrate, default_target_buffer, default_latency_limit]
        
        FRAME_LEN = 0.04
        SEG_NUM_FRAME = 50
        seg_data_size = sum(S_send_data_size[-50:])
        seg_bitrate = seg_data_size / (SEG_NUM_FRAME * FRAME_LEN)
        for i in range(self.NUM_LEVELS):
            seg_bitrate_level_i = seg_bitrate * (self.BIT_RATE_LEVEL[i] / self.BIT_RATE_LEVEL[self.past_decisions[-1]])
            self.past_actual_bitrate[i].append(seg_bitrate_level_i)
            if len(self.past_predicted_bitrate[i]) == 0:
                self.past_predicted_bitrate[i].append(self.past_actual_bitrate[i][-1])

        lmax = 30
        SCslow = 2 / (lmax + 1)
        lmin = 2
        SCfast = 2 / (lmin + 1)
        for i in range(self.NUM_LEVELS):
            if len(self.past_actual_bitrate[i]) < self.ERfactor + 1:
                erfactor = len(self.past_actual_bitrate[i]) - 1
            else:
                erfactor = self.ERfactor
            if erfactor >= 2:
                denominator = 0
                for j in range(erfactor):
                    denominator += abs(self.past_actual_bitrate[i][-1-j] - self.past_actual_bitrate[i][-1-j-1])
                numerator = abs(self.past_actual_bitrate[i][-1] - self.past_actual_bitrate[i][-1-erfactor])
                ER_level_i = numerator / denominator
            else:
                ER_level_i = 0.5
            SC_level_i = (ER_level_i * (SCfast - SCslow) + SCslow) ** 2
            predicted_next_bitrate_level_i = (1 - SC_level_i) * self.past_predicted_bitrate[i][-1] + SC_level_i * self.past_actual_bitrate[i][-1]
            self.past_predicted_bitrate[i].append(predicted_next_bitrate_level_i)
        
        B0min = 0.3
        B0max = 1.0
        B1min = 0.5
        target_buffer = 0
        if self.target_buffer_factor == 1:
            if S_buffer_size[-1] >= B0min and S_buffer_size[-1] < B0max:
                target_buffer = 1
            else:
                target_buffer = 0
        else:
            target_buffer = 0
        
        if self.target_buffer_factor == 1:
            if S_buffer_size[-1] < B1min:
                next_playback_rate = 0.95
            elif S_buffer_size[-1] >= B0max:
                next_playback_rate = 1.05
            else:
                next_playback_rate = 1.0
        else:
            if S_buffer_size[-1] < B0min:
                next_playback_rate = 0.95
            elif S_buffer_size[-1] >= B0max:
                next_playback_rate = 1.05
            else:
                next_playback_rate = 1.0

        if (S_send_data_size[-1] / S_time_interval[-1]) > 1750000:
            throughput_factor = 1
        elif (S_send_data_size[-1] / S_time_interval[-1]) < 1000000:
            throughput_factor = 5
        else:
            throughput_factor = self.throughput_factor

        estimated_throughput = 0
        for i in range(throughput_factor):
            if S_time_interval[-1-i] != 0:
                estimated_throughput += ((S_send_data_size[-1-i] / S_time_interval[-1-i]) * (throughput_factor - i))
        estimated_throughput = estimated_throughput / ((1 + throughput_factor) * throughput_factor / 2)
        self.throughput.append(estimated_throughput)
        
        if estimated_throughput > 2500000:
            Bth = 0.3
        elif estimated_throughput > 2000000:
            Bth = 0.5
        elif estimated_throughput < 700000:
            Bth = 1.5
        elif estimated_throughput < 1250000:
            Bth = 1.25
        else:
            Bth = self.Bth
        # Bth = self.Bth

        T_next_seg = []
        B_next_seg = []
        self.past_N_nst.append(cdn_newest_id)
        min_D = 1000000
        quality_level = 0
        for level in range(self.NUM_LEVELS):
            d = SEG_NUM_FRAME * FRAME_LEN
            T_next_seg.append(self.past_predicted_bitrate[level][-1] * d / estimated_throughput)
            B_next_seg.append(max(S_buffer_size[-1] + d - next_playback_rate * T_next_seg[level], 0))
            v_next_seg = self.beta_factor * (self.past_N_nst[-1] - self.past_N_nst[-2]) * FRAME_LEN / sum(S_time_interval[-50:])
            D_cdn_next_seg = max((self.past_N_nst[-1] - download_id) * FRAME_LEN + v_next_seg * T_next_seg[level] - d, 0)
            D = B_next_seg[level] + D_cdn_next_seg
            if D <= min_D and B_next_seg[level] > Bth:
                min_D = D
                quality_level = level
        
        if self.latency_factor == 4:
            latency_limit = 4
        else:
            latency_limit = (0.001 * self.BIT_RATE_LEVEL[quality_level] + 0.5) * FRAME_LEN / 0.01

        return [quality_level, target_buffer, latency_limit]

    def get_params(self):
    # get your params
        your_params = []
        return your_params
