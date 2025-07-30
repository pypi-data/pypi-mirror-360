# this tools use to merge lines after cv2.houghlinesp. now the code is the best effet in the Internet. 
# The main function is merge_lines Funtion.




import numpy as np 
    
# from : https://stackoverflow.com/questions/45531074/how-to-merge-lines-after-houghlinesp
class HoughBundler:
    '''Clasterize and merge each cluster of cv.HoughLinesP() output
    a = HoughBundler()
    foo = a.process_lines(houghP_lines, binary_image)
    '''

    def get_orientation(self, line):
        '''get orientation of a line, using its length
        https://en.wikipedia.org/wiki/Atan2
        '''
        orientation = math.atan2(abs((line[0] - line[2])), abs((line[1] - line[3])))
        return math.degrees(orientation)

    def checker(self, line_new, groups, min_distance_to_merge, min_angle_to_merge):
        '''Check if line have enough distance and angle to be count as similar
        '''
        for group in groups:
            # walk through existing line groups
            for line_old in group:
                # check distance
                if self.get_distance(line_old, line_new) < min_distance_to_merge:
                    # check the angle between lines
                    orientation_new = self.get_orientation(line_new)
                    orientation_old = self.get_orientation(line_old)
                    # if all is ok -- line is similar to others in group
                    if abs(orientation_new - orientation_old) < min_angle_to_merge:
                        group.append(line_new)
                        return False
        # if it is totally different line
        return True

    def distance_to_line(self, point, line):
        """Get distance between point and line
        https://stackoverflow.com/questions/40970478/python-3-5-2-distance-from-a-point-to-a-line
        """
        px, py = point
        x1, y1, x2, y2 = line
        x_diff = x2 - x1
        y_diff = y2 - y1
        num = abs(y_diff * px - x_diff * py + x2 * y1 - y2 * x1)
        den = math.sqrt(y_diff**2 + x_diff**2)
        return num / den

    def get_distance(self, a_line, b_line):
        """Get all possible distances between each dot of two lines and second line
        return the shortest
        """
        dist1 = self.distance_to_line(a_line[:2], b_line)
        dist2 = self.distance_to_line(a_line[2:], b_line)
        dist3 = self.distance_to_line(b_line[:2], a_line)
        dist4 = self.distance_to_line(b_line[2:], a_line)

        return min(dist1, dist2, dist3, dist4)

    def merge_lines_pipeline_2(self, lines):
        'Clusterize (group) lines'
        groups = []  # all lines groups are here
        # Parameters to play with
        min_distance_to_merge = 30
        min_angle_to_merge = 30
        # first line will create new group every time
        groups.append([lines[0]])
        # if line is different from existing gropus, create a new group
        for line_new in lines[1:]:
            if self.checker(line_new, groups, min_distance_to_merge, min_angle_to_merge):
                groups.append([line_new])

        return groups

    def merge_lines_segments1(self, lines):
        """Sort lines cluster and return first and last coordinates
        """
        orientation = self.get_orientation(lines[0])

        # special case
        if(len(lines) == 1):
            return [lines[0][:2], lines[0][2:]]

        # [[1,2,3,4],[]] to [[1,2],[3,4],[],[]]
        points = []
        for line in lines:
            points.append(line[:2])
            points.append(line[2:])
        # if vertical
        if 45 < orientation < 135:
            #sort by y
            points = sorted(points, key=lambda point: point[1])
        else:
            #sort by x
            points = sorted(points, key=lambda point: point[0])

        # return first and last point in sorted group
        # [[x,y],[x,y]]
        return [points[0], points[-1]]

    def process_lines(self, lines, img=None):
        '''Main function for lines from cv.HoughLinesP() output merging
        for OpenCV 3
        lines -- cv.HoughLinesP() output
        img -- binary image
        '''
        lines_x = []
        lines_y = []
        # for every line of cv.HoughLinesP()
        for line_i in lines:
                orientation = self.get_orientation(line_i)
                # if vertical
                if 45 < orientation < 135:
                    lines_y.append(line_i)
                else:
                    lines_x.append(line_i)

        lines_y = sorted(lines_y, key=lambda line: line[1])
        lines_x = sorted(lines_x, key=lambda line: line[0])
        merged_lines_all = []

        # for each cluster in vertical and horizantal lines leave only one line
        for i in [lines_x, lines_y]:
                if len(i) > 0:
                    groups = self.merge_lines_pipeline_2(i)
                    merged_lines = []
                    for group in groups:
                        merged_lines.append(self.merge_lines_segments1(group))

                    merged_lines_all.extend(merged_lines)

        return merged_lines_all
    
    







# def get_atan2( line):
#     '''get orientation of a line, using its length
#     https://en.wikipedia.org/wiki/Atan2
#     '''
#     orientation = math.atan2((line[1] - line[3]), (line[0] - line[2]))
#     return orientation



def get_orientation( line):
    '''get orientation of a line, using its length
    https://en.wikipedia.org/wiki/Atan2
    '''
    orientation = math.atan2((line[1] - line[3]), (line[0] - line[2]))
    degree=math.degrees(orientation)
    if degree==0:
        degree=180 # when we merge lines. if degree ==0. its weights is waisted. set 180 better .
    if degree<0:
        degree+=180
    if  178<degree<180:
         degree-=180
    # orientation=abs(orientation) # we set radius in  [0,180]
    return degree


def point_to_line_distance(p,line):
    # input: point:(x,y), line (x1,y1,x2,y2)
    # output: the distance between point and line
    x,y=p
    x1,y1,x2,y2=line
    vec1=(x-x1),(y-y1)
    vec2=(x2-x1),(y2-y1)
    vec2_norm=(vec2[0]**2+vec2[1]**2)**0.5
    
    vec1_xtimes_vec2=vec1[0]*vec2[1]-vec2[0]*vec1[1]
    dis=abs(vec1_xtimes_vec2/vec2_norm)
    return dis
def line_norm2(line):
      x1,y1,x2,y2=line
      return  ((x2-x1)**2+(y2-y1)**2)**0.5
def vec_norm2(v):
      x1,y1=v
      return  ((x1)**2+(y1)**2)**0.5


def line_to_line_distance(line1,line2):
    dis1=point_to_line_distance((line1[0],line1[1]),line2)
    dis2=point_to_line_distance((line1[2],line1[3]),line2)
    return min(dis1,dis2)




def check_two_line_whether_coincide(line1,line2, slope_tolerent=0.2,dis_tolerent=3):
    # line1: x1,y1,x2,y2      x1,y1 means first point of line1  ; x2,y2 means second point of line1
    max_slope=70
    x1,y1,x2,y2=line1
    x3,y3,x4,y4=line2
    slope1=cal_slope(line1)
    slope2=cal_slope(line2)
    if slope1 and slope1>max_slope:
      slope1=max_slope
    if slope1 and slope1<-max_slope:
      slope1=max_slope
    if slope2 and slope2>max_slope:
      slope2=max_slope
    if slope2 and slope2<-max_slope:
      slope2=max_slope
    
    #step1: check slope whetether same
    if slope1!=None and slope2!=None and abs(slope1-slope2)>slope_tolerent:
        return False
    if  slope1==None and slope2!=None and slope2<max_slope:
        return False    
    if  slope2==None and slope1!=None and slope1<max_slope:
        return False    
    
    
    if slope1!=None and slope2!=None and abs(slope1-slope2)<slope_tolerent:
       dis=line_to_line_distance(line1,line2)
       
       if dis<=dis_tolerent:
         return True
    if  slope1==None and  slope2==None:
        dis=line_to_line_distance(line1,line2)
        if dis<=dis_tolerent:
         return True
       
def distance_between_2_point(p1,p2):
   v=p2[0]-p1[0],p2[1]-p1[1]
   return vec_norm2(v)       
       

def point_to_line_segment_distance(p,line):  
  vec1=p[0]-line[0],p[1]-line[1]
  vec2=line[2]-line[0],line[3]-line[1]
  candidate_distance=[]
  vec2_hadmard_vec1=vec2[0]*vec1[0]+vec2[1]*vec1[1]
  
  vec3=p[0]-line[2],p[1]-line[3]
  vec4=line[0]-line[2],line[1]-line[3]
  candidate_distance=[]
  vec2_hadmard_vec1next=vec3[0]*vec4[0]+vec3[1]*vec4[1]
  
  
  
  
  if vec2_hadmard_vec1>=0 and vec2_hadmard_vec1next>=0: # means vertical point in line .
     candidate_distance.append(point_to_line_distance(p,line))
  candidate_distance.append(distance_between_2_point(p, (line[0],line[1])))
  candidate_distance.append(distance_between_2_point(p, (line[2],line[3])))
  return  min(candidate_distance)
       
       
def line_segment_to_line_segment_distance(line1,line2):
  a=point_to_line_segment_distance((line1[0],line1[1]),line2)
  b=point_to_line_segment_distance((line1[2],line1[3]),line2)
  c=point_to_line_segment_distance((line2[0],line2[1]),line1)
  d=point_to_line_segment_distance((line2[2],line2[3]),line1)
  return  min (a,b,c,d)
  
  
  pass       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       

       
# 查看2个线段是不是可以判定为重叠. check two segemnt whether can merge to one.
def check_two_line_segment_whether_coincide(line1,line2, slope_tolerent=10,dis_tor=15):
    # line1: x1,y1,x2,y2      x1,y1 means first point of line1  ; x2,y2 means second point of line1
    max_slope=70
    x1,y1,x2,y2=line1
    x3,y3,x4,y4=line2
    ori1=get_orientation(line1) # use tan2function powerful
    ori2=get_orientation(line2)

    ori11=ori1+180
    ori22=ori2+180
    
    diffori= min(abs(ori1-ori2),abs(ori1-ori22),abs(ori11-ori2),abs(ori11-ori22))
    #step1: check slope whetether same
    if diffori<slope_tolerent and line_segment_to_line_segment_distance(line1,line2)<=dis_tor:
        return True
    return False

    
    

       
       
       
       
def lines_have_2_lines_can_merge(lines):
    for i,line in enumerate(lines):
        for j,l in enumerate(lines):

              if i!=j and check_two_line_segment_whether_coincide(line,l,dis_tolerent=3):
                 return i,j
    return False


# some mistake algorithm:
# 



def merge_lines_old(lines):#=======直线融合.
  # lines: [ line1,line2,...]
  # 
    while 1: 
        tmp=  lines_have_2_lines_can_merge(lines)
        if tmp:
                i,k=lines[tmp[0]],lines[tmp[1]]
                lines[tmp[0]][0] = min(i[0], k[0])  # 合并
                lines[tmp[0]][1] = min(i[1], k[1])
                lines[tmp[0]][2] = max(i[2], k[2])
                lines[tmp[0]][3] = max(i[3], k[3])
                lines.pop(tmp[1])
        else:
          break
    return lines
       
def merge_lines_segments1( lines):# this algorithm cannot compute well in the case: 
        '''
              [1,0,0,1],
      [2,0,0,2],
      [3,0,0,3],
        '''
        """Sort lines cluster and return first and last coordinates
        """
        orientation = get_orientation(lines[0])

        # special case
        if(len(lines) == 1):
            return [lines[0][:2], lines[0][2:]]

        # [[1,2,3,4],[]] to [[1,2],[3,4],[],[]]
        points = []
        for line in lines:
            points.append(line[:2])
            points.append(line[2:])
        # if vertical
        if 45 < orientation < 135:
            #sort by y
            points = sorted(points, key=lambda point: point[1])
        else:
            #sort by x
            points = sorted(points, key=lambda point: point[0])

        # return first and last point in sorted group
        # [[x,y],[x,y]]
        return [points[0], points[-1]]
import math
#=My Main function!!!!!!
def merge_lines(lines,slope_tolerent=10,dis_tor=5):#=======直线融合.
  # lines: [ line1,line2,...]
  # 
  # step1: cluster:
    for dex,i in enumerate(lines):
        if i[0]>i[2]:
            lines[dex]=[lines[dex][2],lines[dex][3],lines[dex][0],lines[dex][1]]
    
    def put_line_to_cluster(line, clusters):
      pass
      for d,c in enumerate(clusters):
         for line_old in c:
            if check_two_line_segment_whether_coincide(line,line_old,slope_tolerent= slope_tolerent,dis_tor=dis_tor):
               clusters[d].append(line)
               return clusters
      clusters.append([line])
      

      
      
      
      
      
      return clusters
    if len(lines)==1 or 0:
      return [lines]
  
  
    # this cluster algorithm is not enough!!!!!!
    if 1:
        clusters=[] # 
        clusters.append([lines[0]])#put in first lines as first cluster
        
        
        for i in lines[1:]:
            clusters=put_line_to_cluster(i,clusters)
    #========================
    
    # here is the next version of cluster.
    #first we set all line a cluster. we check every time to merge 2 cluster.
    clusters

    def check_all_clusters(slope_tolerent=slope_tolerent,dis_tor=dis_tor):# if we 2 cluster can merge, we return, and conpute from begin.
        for i in range(len(clusters)):
            for j in range(len(clusters)):
                if i!=j and check_and_merge_2_cluster(i,j,slope_tolerent=slope_tolerent,dis_tor=dis_tor):
                    clusters[i]+=clusters[j] # we do merge
                    clusters.pop(j) # remove useless one. 
                    return True
        return False
                
                
                
                
    def check_and_merge_2_cluster(cluster_dex1,cluster_dex2,slope_tolerent=slope_tolerent,dis_tor=dis_tor):
        # if 2cluster can merge we merge. and return
        if cluster_dex1==cluster_dex2:
            return False
        a=clusters[cluster_dex1]
        b=clusters[cluster_dex2]
        for  dex,i in enumerate(a):
            for  dex2,j in enumerate(b):
                 if check_two_line_segment_whether_coincide(i,j,slope_tolerent=slope_tolerent,dis_tor=dis_tor):

                     return True
                 
    # check_two_line_segment_whether_coincide(clusters[1][0],clusters[2][0])
    # line_segment_to_line_segment_distance(clusters[1][0],clusters[2][0])
    # abs(get_orientation(clusters[1][0])-get_orientation(clusters[2][0]))
    
    while check_all_clusters():
        continue
    
    
    
    
    #========this is useful to check wheteher our cluster algorithm is right!!!!!!!
    if 0: # check clusters pic: # only open for debug!!!!!!!!!!!
            import cv2
            # compute how big the screen
            # 
            maxx=[]
            maxy=[]
            for i in clusters:
                for j in i:
                    maxx.append(j[0])
                    maxx.append(j[2])
                    maxy.append(j[1])
                    maxy.append(j[3])
            a=max(maxx)+300
            b=max(maxy)+300
            
            
            for dex,i in enumerate(clusters):
                line_image = np.ones([b,a])*255 # 空白白板
                if lines is not None:
                    for line in i:
                        x1, y1, x2, y2 = line
                        cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.imwrite(f'debug_cluster{dex}.png',line_image)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
                 
    
    
    

               
    def calc_slope( line):
      '''get orientation of a line, using its length
      https://en.wikipedia.org/wiki/Atan2
      '''
      orientation =(line[1] - line[3])/ (line[0] - line[2]+1e-10)
      # line_slope can be very big, so the solution may vary too big.we clip it. 
      if orientation>30:
          orientation=30
      if orientation<-30:
            orientation=-30
      
      return orientation
    def merge_a_c_to_a_line(c):
      # given a cluster of lines  we compute the merged line of them, and return it.
      # step 1  :   we first compute avg of tan2
      avg_atan2=[]
      wegiths=[]
      for i in c:
         avg_atan2.append(get_orientation(i))
         wegiths.append(vec_norm2((i[2]-i[0],i[3]-i[1]))**3) # we set weights = length**2
    #   avg_atan2=sum(avg_atan2)/len(avg_atan2) # use weight by lines length
      out=0
      for i in range(len(avg_atan2)):
        out+=avg_atan2[i]*wegiths[i]/sum(wegiths)

      avg_atan2=out
      #==角度改斜率
      avg_atan2=math.tan(avg_atan2*math.pi/180)
      

      
      
      
      
      
      
      
      
      
      
      # step2: we compute norm vector
      if avg_atan2==0:
          norm_slope=9999999
      else:
        norm_slope=-1/avg_atan2
      if norm_slope==float('inf'):
           norm_slope=9999
      if norm_slope==-float('inf'):
           norm_slope=-9999

      # projection on norm_vec
      first_mid_p=(c[0][0]+c[0][2])/2,(c[0][1]+c[0][3])/2
      norm_vec=[1,norm_slope]
      
      norm_vec[0],norm_vec[1]=norm_vec[0]/vec_norm2(norm_vec),norm_vec[1]/vec_norm2(norm_vec)
      all_p=[]
      for i in c:
         all_p.append((i[0],i[1]))
         all_p.append((i[2],i[3]))
      all_p_projection=[]
      for i in all_p:
         projection= i[0]*norm_vec[0]+i[1]*norm_vec[1]
         projection_length= projection/ vec_norm2(norm_vec)
         projection_corodinate=projection_length*norm_vec[0],projection_length*norm_vec[1]
         all_p_projection.append(projection_corodinate)
      tmpx=sum([i[0] for i in all_p_projection])/len(all_p_projection)
      tmpy=sum([i[1] for i in all_p_projection])/len(all_p_projection)
      
      #weighted:
      tmpx=0
      tmpy=0
      wegiths2=[]
      for i in wegiths:
           wegiths2.append(i)
           wegiths2.append(i)
      for i in range(len(wegiths2)):
          tmpx+=all_p_projection[i][0]*wegiths2[i]/sum(wegiths2)
      for i in range(len(wegiths2)):
          tmpy+=all_p_projection[i][1]*wegiths2[i]/sum(wegiths2)
      
      
      projection_mid=[tmpx,tmpy]

      # projection on direction_vec

      dire_vec=[1,avg_atan2]
      dire_vec[0],dire_vec[1]=dire_vec[0]/vec_norm2(dire_vec),dire_vec[1]/vec_norm2(dire_vec)

      all_p=[]
      for i in c:
         all_p.append((i[0],i[1]))
         all_p.append((i[2],i[3]))
      all_p_projection=[]
      tmp=[]
      for i in all_p:
         projection= i[0]*dire_vec[0]+i[1]*dire_vec[1]
         projection_length= projection/ vec_norm2(dire_vec)
         tmp.append(projection_length)
        #  projection_corodinate=projection_length*dire_vec[0],projection_length*dire_vec[1]
        #  all_p_projection.append(projection_corodinate)
      mini=min(tmp)
      maxi=max(tmp)
      best_line_project_on_directionvec=mini*dire_vec[0],mini*dire_vec[1],maxi*dire_vec[0],maxi*dire_vec[1]

      
      final_corordinate=projection_mid[0]+best_line_project_on_directionvec[0],projection_mid[1]+best_line_project_on_directionvec[1],projection_mid[0]+best_line_project_on_directionvec[2],projection_mid[1]+best_line_project_on_directionvec[3]
      
      def near(i):
          return int(i+0.5)
      final_corordinate=[near(i) for i in final_corordinate]

      return final_corordinate
    res=[]
    for d,i in enumerate(clusters):
        test1=merge_a_c_to_a_line(i)
        res.append(test1)
    test2=[get_orientation(i) for i in res]
    # check_two_line_segment_whether_coincide(res[3],res[11])
    return res
    
    
    
  
    # while 1: 
    #     tmp=  lines_have_2_lines_can_merge(lines)
    #     if tmp:
    #             i,k=lines[tmp[0]],lines[tmp[1]]
    #             lines[tmp[0]][0] = min(i[0], k[0])  # 合并
    #             lines[tmp[0]][1] = min(i[1], k[1])
    #             lines[tmp[0]][2] = max(i[2], k[2])
    #             lines[tmp[0]][3] = max(i[3], k[3])
    #             lines.pop(tmp[1])
    #     else:
    #       break
    return clusters[2]
    
    
    
    
    
    
    
    
    
    
if __name__ == "__main__":









    print("now----test_my_function_better_performance!!!!!!!!!!!!!NOW is the best output in the internet")
    print(merge_lines([
      [1,0,0,1],
      [2,0,0,2],
      [3,0,0,3],
      [30,0,0,30],
      [30,0,0,30],
      [30,0,0,30],
      [30,1,1,30],
      [30,11,11,30],
      
      
    ]))

    # print(point_to_line_segment_distance( [799, 590],(798, 232,798,23)))
    print(point_to_line_segment_distance( [798, 23],(799, 590, 799, 308)))