# this tools use to merge lines after cv2.houghlinesp. now the code is the best effet in the Internet. 
# The main function is merge_lines Funtion.




    
    
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
    
    







def get_atan2( line):
    '''get orientation of a line, using its length
    https://en.wikipedia.org/wiki/Atan2
    '''
    orientation = math.atan2((line[1] - line[3]), (line[0] - line[2]))
    return orientation



def get_orientation( line):
    '''get orientation of a line, using its length
    https://en.wikipedia.org/wiki/Atan2
    '''
    orientation = math.atan2((line[1] - line[3]), (line[0] - line[2]))
    orientation=abs(orientation) # we set radius in  [0,180]
    return math.degrees(orientation)
def cal_scope(line):
    # input: line
    # output: line_scope
    x1, y1, x2, y2 = line
    # 检查是否垂直
    if x2 - x1 == 0:
        return None
    
    return (y2 - y1) / (x2 - x1)

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




def check_two_line_whether_coincide(line1,line2, scope_tolerent=0.2,dis_tolerent=3):
    # line1: x1,y1,x2,y2      x1,y1 means first point of line1  ; x2,y2 means second point of line1
    max_scope=70
    x1,y1,x2,y2=line1
    x3,y3,x4,y4=line2
    scope1=cal_scope(line1)
    scope2=cal_scope(line2)
    if scope1 and scope1>max_scope:
      scope1=max_scope
    if scope1 and scope1<-max_scope:
      scope1=max_scope
    if scope2 and scope2>max_scope:
      scope2=max_scope
    if scope2 and scope2<-max_scope:
      scope2=max_scope
    
    #step1: check scope whetether same
    if scope1!=None and scope2!=None and abs(scope1-scope2)>scope_tolerent:
        return False
    if  scope1==None and scope2!=None and scope2<max_scope:
        return False    
    if  scope2==None and scope1!=None and scope1<max_scope:
        return False    
    
    
    if scope1!=None and scope2!=None and abs(scope1-scope2)<scope_tolerent:
       dis=line_to_line_distance(line1,line2)
       
       if dis<=dis_tolerent:
         return True
    if  scope1==None and  scope2==None:
        dis=line_to_line_distance(line1,line2)
        if dis<=dis_tolerent:
         return True
       
def distance_between_2_point(p1,p2):
   v=p2[0]-p1[0],p2[1]-p1[1]
   return vec_norm2(v)       
       

def point_to_line_segment_distance(p,line):  
  vec1=line[0]-p[0],line[1]-p[1]
  vec2=line[2]-line[0],line[3]-line[1]
  candidate_distance=[]
  vec2_hadmard_vec1=vec2[0]*vec1[0]+vec2[1]*vec1[1]
  if vec2_hadmard_vec1>=0: # means vertical point in line .
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
def check_two_line_segment_whether_coincide(line1,line2, scope_tolerent=10,dis_tolerent=3):
    # line1: x1,y1,x2,y2      x1,y1 means first point of line1  ; x2,y2 means second point of line1
    max_scope=70
    x1,y1,x2,y2=line1
    x3,y3,x4,y4=line2
    scope1=get_orientation(line1) # use tan2function powerful
    scope2=get_orientation(line2)

    
    #step1: check scope whetether same
    if abs(scope1-scope2)<scope_tolerent and line_segment_to_line_segment_distance(line1,line2)<=dis_tolerent:
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
    
#=My Main function!!!!!!
def merge_lines(lines,scope_tolerent=10,dis_tor=5):#=======直线融合.
  # lines: [ line1,line2,...]
  # 
  # step1: cluster:
    
    def put_line_to_cluster(line, clusters):
      pass
      for d,c in enumerate(clusters):
         for line_old in c:
            if check_two_line_segment_whether_coincide(line,line_old,scope_tolerent= scope_tolerent,dis_tolerent=dis_tor):
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

    def check_all_clusters():# if we 2 cluster can merge, we return, and conpute from begin.
        for i in range(len(clusters)):
            for j in range(len(clusters)):
                if i!=j and check_and_merge_2_cluster(i,j):
                    return True
        return False
                
                
                
                
    def check_and_merge_2_cluster(cluster_dex1,cluster_dex2):
        # if 2cluster can merge we merge. and return
        if cluster_dex1==cluster_dex2:
            return False
        a=clusters[cluster_dex1]
        b=clusters[cluster_dex2]
        for  dex,i in enumerate(a):
            for  dex2,j in enumerate(b):
                 if check_two_line_segment_whether_coincide(i,j):
                     clusters[cluster_dex1]+=clusters[cluster_dex2] # we do merge
                     clusters.pop(cluster_dex2) # remove useless one.
                     return True
                 
    # check_two_line_segment_whether_coincide(clusters[1][0],clusters[2][0])
    # line_segment_to_line_segment_distance(clusters[1][0],clusters[2][0])
    # abs(get_orientation(clusters[1][0])-get_orientation(clusters[2][0]))
    
    while check_all_clusters():
        continue
    
    
    
    
    #========this is useful to check wheteher our cluster algorithm is right!!!!!!!
    if 1: # check clusters pic: # only open for debug!!!!!!!!!!!
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
                 
    
    
    

    print('over cluster')
    print('len(clusters)',len(clusters))
               
    def calc_scope( line):
      '''get orientation of a line, using its length
      https://en.wikipedia.org/wiki/Atan2
      '''
      orientation =(line[1] - line[3])/ (line[0] - line[2]+1e-10)
      # line_scope can be very big, so the solution may vary too big.we clip it. 
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
         avg_atan2.append(calc_scope(i))
         wegiths.append(vec_norm2((i[2]-i[0],i[3]-i[1]))**2) # we set weights = length**2
    #   avg_atan2=sum(avg_atan2)/len(avg_atan2) # use weight by lines length
      out=0
      for i in range(len(avg_atan2)):
        out+=avg_atan2[i]*wegiths[i]/sum(wegiths)

      avg_atan2=out
      
      
      
      
      
      
      
      
      
      
      
      # step2: we compute norm vector
      norm_scope=-1/avg_atan2
      if norm_scope==float('inf'):
           norm_scope=9999
      if norm_scope==-float('inf'):
           norm_scope=-9999

      # projection on norm_vec
      first_mid_p=(c[0][0]+c[0][2])/2,(c[0][1]+c[0][3])/2
      norm_vec=[1,norm_scope]
      
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
      final_corordinate=[int(i) for i in final_corordinate]

      return final_corordinate
    res=[]
    for d,i in enumerate(clusters):
        test1=merge_a_c_to_a_line(i)
        res.append(test1)
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
    
    
    
    
    
    
    
    
    
    
    
import math
import numpy as np
def check_overlap(line1, line2):
    combination = np.array([line1,
                            line2,
                            [line1[0], line1[1], line2[0], line2[1]],
                            [line1[0], line1[1], line2[2], line2[3]],
                            [line1[2], line1[3], line2[0], line2[1]],
                            [line1[2], line1[3], line2[2], line2[3]]])
    distance = np.sqrt((combination[:,0] - combination[:,2])**2 + (combination[:,1] - combination[:,3])**2)
    max = np.amax(distance)
    overlap = distance[0] + distance[1] - max 
    endpoint = combination[np.argmax(distance)]
    print(1)
    return (overlap >= 0), endpoint #replace 0 with the value of distance between 2 collinear lines

def mergeLine(line_list):
    #convert (x1, y1, x2, y2) formm to (r, alpha) form
    A = line_list[:,1] - line_list[:,3]
    B = line_list[:,2] - line_list[:,0]
    C = line_list[:,0]*line_list[:,3] - line_list[:,2]*line_list[:,1]
    r = np.divide(np.abs(C), np.sqrt(A*A+B*B))
    alpha = (np.arctan2(-B,-A) + math.pi) % (2*math.pi) - math.pi
    r_alpha = np.column_stack((r, alpha))

    #prepare some variables to keep track of lines looping
    r_bin_size = 10 #maximum distance to treat 2 lines as one
    alpha_bin_size = 0.15 #maximum angle (radian) to treat 2 lines as one
    merged = np.zeros(len(r_alpha), dtype=np.uint8)
    line_group = np.empty((0,4), dtype=np.int32)
    group_count = 0

    for line_index in range(len(r_alpha)): 
        if merged[line_index] == 0: #if line hasn't been merged yet
            merged[line_index] = 1
            line_group = np.append(line_group, [line_list[line_index]], axis=0)
            for line_index2 in range(line_index+1,len(r_alpha)):
                if merged[line_index2] == 0:
                    #calculate the differences between 2 lines by r and alpha
                    dr = abs(r_alpha[line_index,0] - r_alpha[line_index2,0])
                    dalpha = abs(r_alpha[line_index,1] - r_alpha[line_index2,1])
                    if (dr<r_bin_size) and (dalpha<alpha_bin_size): #if they are close, they are the same line, so check if they are overlap
                        overlap, endpoints = check_overlap(line_group[group_count], line_list[line_index2])
                        if overlap:
                            line_group[group_count] = endpoints
                            merged[line_index2] = 1
            group_count += 1
    return line_group
    
    
    
    
    
    
if __name__ == "__main__":
    print(cal_scope((0,0,1,1)))
    print(point_to_line_distance((-1,0),(0,1,1,0)))
    print(check_two_line_whether_coincide((0,0,1,1),(1,1,2,2)))
    print(check_two_line_whether_coincide((0,0,0,1),(1,1,1,2)))
    print(check_two_line_whether_coincide((0,0,0,1),(0,0,0,2)))



    print(1)
    linesss=np.array([
      [1,0,0,1],
      [2,0,0,2],
      [3,0,0,3],
      
      
    ])
    print(
      mergeLine(
        np.array([
      [1,0,0,1],
      [2,0,0,2],
      [3,0,0,3],
      
      
    ])
        
        
        
      )
    )


    a = HoughBundler()
    foo = a.process_lines(linesss)
    print(
foo
      
      
      
    )
    print(1)




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

